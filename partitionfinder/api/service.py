"""FastAPI backend service (Phase 2.2 — Local First).

This API provides:
- Job submission
- Progress/status polling
- Result retrieval
- Live log streaming over WebSocket

Design notes:
- Jobs are persisted on the local filesystem under `.pf_jobs/` by default.
- Execution uses `partitionfinder.core.run_folder` in a background thread.
- Scientific behavior is unchanged; this is orchestration only.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
import threading
import time
from contextlib import suppress
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional
from uuid import uuid4

import multiprocessing

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel, Field

import re

from partitionfinder.core import run_folder


JobState = Literal["queued", "running", "succeeded", "failed"]


def _parse_cpus_from_argv(argv: list[str]) -> int | None:
    """Best-effort extraction of legacy process count from argv.

    We persist the effective legacy argv in JobMetadata. This helper allows the
    UI to display whether parallelism was enabled without re-deriving it from
    request state.
    """
    for i, tok in enumerate(argv):
        if tok in {"-p", "--processes", "--processors"}:
            if i + 1 >= len(argv):
                return None
            try:
                return int(argv[i + 1])
            except ValueError:
                return None
        if tok.startswith("--processes="):
            try:
                return int(tok.split("=", 1)[1])
            except ValueError:
                return None
        if tok.startswith("--processors="):
            try:
                return int(tok.split("=", 1)[1])
            except ValueError:
                return None
    return None


def _utc_now_iso() -> str:
    # Use timezone-aware UTC timestamps to avoid deprecated utcnow().
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True)
class JobMetadata:
    id: str
    created_at: str
    updated_at: str
    state: JobState
    datatype: str
    input_folder: str
    working_folder: str
    argv: list[str]
    pid: Optional[int] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None
    progress_pct: Optional[float] = None  # For future enhancement


class JobRequest(BaseModel):
    folder: str = Field(..., description="Path to folder containing partition_finder.cfg")
    datatype: Literal["DNA", "protein", "morphology"] = "DNA"
    cpus: int = Field(
        default=1,
        ge=1,
        le=256,
        description=(
            "Opt-in parallelism (maps to legacy '-p <cpus>'). Defaults to 1 to preserve baseline behavior. "
            "Ignored if you explicitly pass '-p'/'--processes' in args (conflict will error)."
        ),
    )
    args: list[str] = Field(default_factory=list, description="Legacy CLI args (e.g., ['-p','1','-n','-f'])")
    copy_input: bool = Field(
        default=True,
        description="If true, copy the input folder into an isolated job working dir.",
    )
    overrides: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Optional overrides applied to the config (.cfg) in the working folder before running. "
            "Supported keys: models, model_selection, search, branchlengths."
        ),
    )


class JobSubmitResponse(BaseModel):
    id: str


def _effective_argv(req: JobRequest) -> list[str]:
    """Compute the legacy argv list for a job request.

        Guardrails:
        - If args is empty, we inject '-p <cpus>' (cpus defaults to 1) to stabilize
            baseline behavior across environments.
        - If args is not empty, we only inject when the user opts into parallelism
            (cpus != 1), to avoid surprising callers that already specify legacy flags.
    - Backwards compatible: if args explicitly provides '-p/--processes', we do
      not inject a second value.
    - Conflict guardrail: if cpus is explicitly set to a non-default value and
      args also provides '-p/--processes', we error.
    - Repro guardrail: if effective cpus > 1, require copy_input=True to avoid
      concurrent writes into a shared input folder.
    """

    def parse_explicit_processes(args: list[str]) -> int | None:
        for i, tok in enumerate(args):
            if tok in {"-p", "--processes", "--processors"}:
                if i + 1 >= len(args):
                    raise ValueError("'-p/--processes' requires a value")
                try:
                    return int(args[i + 1])
                except ValueError as e:
                    raise ValueError("'-p/--processes' value must be an integer") from e
            if tok.startswith("--processes="):
                try:
                    return int(tok.split("=", 1)[1])
                except ValueError as e:
                    raise ValueError("'--processes=' value must be an integer") from e
            if tok.startswith("--processors="):
                try:
                    return int(tok.split("=", 1)[1])
                except ValueError as e:
                    raise ValueError("'--processors=' value must be an integer") from e
        return None

    argv = list(req.args)
    explicit = parse_explicit_processes(argv)

    if explicit is not None:
        if req.cpus != 1 and explicit != int(req.cpus):
            raise ValueError(
                "cpus conflicts with explicit '-p/--processes' in args; please use one or ensure they match"
            )
        effective_cpus = explicit
    else:
        effective_cpus = int(req.cpus)
        should_inject = (len(argv) == 0) or (effective_cpus != 1)
        if should_inject:
            argv = ["-p", str(effective_cpus), *argv]

    if effective_cpus > 1 and not req.copy_input:
        raise ValueError("cpus > 1 requires copy_input=true for reproducibility")

    return argv


class JobStatusResponse(BaseModel):
    id: str
    state: JobState
    created_at: str
    updated_at: str
    datatype: str | None = None
    input_folder: str | None = None
    cpus: Optional[int] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None


class StopJobResponse(BaseModel):
    status: str
    job_id: str


class JobResultsResponse(BaseModel):
    id: str
    state: JobState
    cpus: Optional[int] = None
    best_scheme_txt: Optional[str] = None
    scheme_data_csv: Optional[str] = None
    analysis_path: Optional[str] = None


class DataBlock(BaseModel):
    name: str
    range: str
    length: Optional[int] = None


class FolderPreviewRequest(BaseModel):
    folder: str = Field(..., description="Path to folder containing partition_finder.cfg")


class FolderBrowseResponse(BaseModel):
    folder: Optional[str] = None


class FolderPreviewResponse(BaseModel):
    folder: str
    cfg_file: str
    alignment: Optional[str] = None
    data_blocks: list[DataBlock] = Field(default_factory=list)


class JobStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def exists(self, job_id: str) -> bool:
        return self.meta_path(job_id).exists()

    def job_dir(self, job_id: str) -> Path:
        return self.root / job_id

    def meta_path(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "meta.json"

    def log_path(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "job.log"

    def write_meta(self, meta: JobMetadata) -> None:
        p = self.meta_path(meta.id)
        # Atomic write so readers never observe a partially-written JSON file.
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        payload = json.dumps(asdict(meta), indent=2)
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, p)

    def read_meta(self, job_id: str, *, retries: int = 5, retry_delay_s: float = 0.02) -> JobMetadata:
        p = self.meta_path(job_id)
        if not p.exists():
            raise KeyError(job_id)

        last_err: Exception | None = None
        for _ in range(max(1, int(retries))):
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
                return JobMetadata(**raw)
            except (OSError, json.JSONDecodeError, ValueError) as e:
                # On Windows, concurrent atomic replace (os.replace) can sometimes race
                # with readers (AV scanners / filesystem semantics). Retry briefly.
                last_err = e
                time.sleep(float(retry_delay_s))

        if last_err is not None:
            raise last_err
        raise RuntimeError("Failed to read job metadata")

    def list_job_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        return [p.name for p in self.root.iterdir() if p.is_dir()]

    def append_log(self, job_id: str, line: str) -> None:
        lp = self.log_path(job_id)
        with self._lock:
            lp.parent.mkdir(parents=True, exist_ok=True)
            with lp.open("a", encoding="utf-8") as f:
                f.write(line)
                if not line.endswith("\n"):
                    f.write("\n")

    def delete_job(self, job_id: str) -> bool:
        """Remove a job and all its artifacts. Returns True if deleted."""
        job_dir = self.job_dir(job_id)
        if not job_dir.exists():
            return False
        with self._lock:
            shutil.rmtree(job_dir, ignore_errors=True)
        return True


def default_job_root() -> Path:
    # Local-first persistence. Use env var to override.
    configured = os.environ.get("PF_JOB_DIR")
    if configured:
        return Path(configured)
    return Path.cwd() / ".pf_jobs"


store = JobStore(default_job_root())


def _copy_folder(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _job_best_scheme_path(working_folder: Path) -> Path:
    return working_folder / "analysis" / "best_scheme.txt"


def _validate_input_folder(folder_path: Path) -> None:
    """Validate the input folder exists and contains required files."""
    if not folder_path.exists():
        raise ValueError(f"Folder not found: {folder_path}")
    if not folder_path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    # Check for partition_finder.cfg or any .cfg file
    cfg_files = list(folder_path.glob("*.cfg"))
    if not cfg_files:
        raise ValueError(
            f"No .cfg file found in {folder_path}. "
            "PartitionFinder requires a partition_finder.cfg file."
        )


def _find_cfg_file(folder_path: Path) -> Path:
    preferred = folder_path / "partition_finder.cfg"
    if preferred.exists() and preferred.is_file():
        return preferred
    cfg_files = sorted(p for p in folder_path.glob("*.cfg") if p.is_file())
    if not cfg_files:
        raise ValueError(
            f"No .cfg file found in {folder_path}. PartitionFinder requires a partition_finder.cfg file."
        )
    return cfg_files[0]


def _apply_cfg_overrides(cfg_path: Path, overrides: dict[str, str]) -> None:
    if not overrides:
        return

    allowed = {"models", "model_selection", "search", "branchlengths"}
    unknown = sorted(set(overrides) - allowed)
    if unknown:
        raise ValueError(f"Unsupported override keys: {', '.join(unknown)}")

    text = cfg_path.read_text(encoding="utf-8", errors="replace")
    original = text

    def replace_kv(key: str, value: str) -> None:
        nonlocal text
        # Replace the first occurrence of `key = ...;` (case-insensitive, line-based).
        pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.*?;\s*$", re.IGNORECASE | re.MULTILINE)
        repl = f"{key} = {value};"
        if pattern.search(text):
            text = pattern.sub(repl, text, count=1)
        else:
            # If the key wasn't found, append a new assignment at the end.
            if not text.endswith("\n"):
                text += "\n"
            text += repl + "\n"

    for k, v in overrides.items():
        replace_kv(k, v)

    if text != original:
        cfg_path.write_text(text, encoding="utf-8")


def _parse_alignment_from_cfg(text: str) -> Optional[str]:
    m = re.search(r"^\s*alignment\s*=\s*(.+?)\s*;\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def _range_length(range_expr: str) -> Optional[int]:
    """Best-effort range length for PF range expressions.

    Supports:
    - 1-490
    - 1622-2243\\3 (codon step)
    - Comma-separated segments
    """
    parts = [p.strip() for p in range_expr.replace(";", "").split(",") if p.strip()]
    total = 0
    any_ok = False

    for part in parts:
        # Step syntax: start-end\step
        m = re.match(r"^\s*(\d+)\s*-\s*(\d+)(?:\\\s*(\d+))?\s*$", part)
        if m:
            a = int(m.group(1))
            b = int(m.group(2))
            step = int(m.group(3)) if m.group(3) else 1
            if b >= a and step >= 1:
                total += ((b - a) // step) + 1
                any_ok = True
            continue

        # Explicit site lists are uncommon in cfg, but handle as fallback.
        nums = [int(x) for x in re.findall(r"\d+", part)]
        if nums:
            total += len(nums)
            any_ok = True

    return total if any_ok else None


def _parse_data_blocks_from_cfg(text: str) -> list[DataBlock]:
    lines = text.splitlines()
    in_blocks = False
    blocks: list[DataBlock] = []

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if re.match(r"^\[\s*data_blocks\s*\]$", line, flags=re.IGNORECASE):
            in_blocks = True
            continue

        if in_blocks and re.match(r"^\[.+\]$", line):
            # Next section.
            break

        if not in_blocks:
            continue

        m = re.match(r"^\s*([^=]+?)\s*=\s*(.+?)\s*;\s*$", raw)
        if not m:
            continue
        name = m.group(1).strip()
        rng = m.group(2).strip()
        blocks.append(DataBlock(name=name, range=rng, length=_range_length(rng)))

    return blocks


def _run_job(job_id: str, store_root: str) -> None:
    # IMPORTANT (Windows): multiprocessing uses spawn, which re-imports this
    # module in the child process. That means any in-process overrides of the
    # module-level `store` (e.g., tests/benchmarks) would be lost.
    #
    # We therefore pass the store root explicitly so the worker always reads
    # and writes job artifacts in the intended location.
    local_store = JobStore(Path(store_root))

    meta = local_store.read_meta(job_id)

    # Capture Python logging output (including legacy engine logs) into the
    # per-job log file so WS streaming shows meaningful progress.
    file_handler = logging.FileHandler(local_store.log_path(job_id), mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(levelname)-8s | %(asctime)s | %(name)-10s | %(message)s")
    )

    root_logger = logging.getLogger("")
    prev_level = root_logger.level
    # Ensure INFO-level logs from legacy modules are not filtered out.
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    local_store.append_log(job_id, f"[{_utc_now_iso()}] Starting job {job_id}")

    stop_heartbeat = threading.Event()

    def heartbeat() -> None:
        # Keep status and logs feeling alive even if the legacy engine is quiet.
        start = time.time()
        last_emit = 0.0
        last_size = -1
        while not stop_heartbeat.wait(1.0):
            with suppress(Exception):
                meta0 = local_store.read_meta(job_id)
                # Touch updated_at so /status reflects activity.
                touched = JobMetadata(
                    **{
                        **asdict(meta0),
                        "updated_at": _utc_now_iso(),
                    }
                )
                local_store.write_meta(touched)

            # Emit a low-frequency heartbeat line only if the log file is otherwise silent.
            with suppress(Exception):
                lp = local_store.log_path(job_id)
                size = lp.stat().st_size if lp.exists() else -1
                now = time.time()
                if size == last_size and (now - last_emit) >= 10.0:
                    elapsed_s = int(now - start)
                    local_store.append_log(job_id, f"[{_utc_now_iso()}] Running... elapsed={elapsed_s}s")
                    last_emit = now
                last_size = size

    hb_thread = threading.Thread(target=heartbeat, name=f"pf-job-heartbeat-{job_id}", daemon=True)
    hb_thread.start()

    try:
        now = _utc_now_iso()
        meta = JobMetadata(
            **{**asdict(meta), "state": "running", "updated_at": now}
        )
        local_store.write_meta(meta)

        # Run analysis. Note: legacy engine uses its own logging; we keep a
        # minimal job log around orchestration steps.
        exit_code = run_folder(
            meta.working_folder,
            datatype=meta.datatype,
            passed_args=meta.argv,
            name="PartitionFinder",
        )

        now = _utc_now_iso()
        final_state: JobState = "succeeded" if exit_code == 0 else "failed"
        meta = JobMetadata(
            **{
                **asdict(meta),
                "state": final_state,
                "updated_at": now,
                "exit_code": int(exit_code),
            }
        )
        local_store.write_meta(meta)
        local_store.append_log(job_id, f"[{_utc_now_iso()}] Finished with exit_code={exit_code}")

    except Exception as e:  # noqa: BLE001
        now = _utc_now_iso()
        local_store.append_log(job_id, f"[{now}] ERROR: {e!r}")
        meta = JobMetadata(
            **{
                **asdict(meta),
                "state": "failed",
                "updated_at": now,
                "exit_code": 1,
                "error": repr(e),
            }
        )
        local_store.write_meta(meta)

    finally:
        stop_heartbeat.set()
        with suppress(Exception):
            hb_thread.join(timeout=2.0)
        root_logger.removeHandler(file_handler)
        root_logger.setLevel(prev_level)
        file_handler.close()


def submit_job(req: JobRequest) -> str:
    src = Path(req.folder).resolve()
    _validate_input_folder(src)

    job_id = uuid4().hex
    job_dir = store.job_dir(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    if req.copy_input:
        working = job_dir / "work"
        _copy_folder(src, working)
    else:
        working = src

    # Apply configuration overrides inside the working folder.
    if req.overrides:
        cfg_path = _find_cfg_file(working)
        _apply_cfg_overrides(cfg_path, req.overrides)

    now = _utc_now_iso()

    argv = _effective_argv(req)

    meta = JobMetadata(
        id=job_id,
        created_at=now,
        updated_at=now,
        state="queued",
        datatype=req.datatype,
        input_folder=str(src),
        working_folder=str(working),
        argv=argv,
    )
    store.write_meta(meta)
    store.append_log(job_id, f"[{now}] Queued job; working_folder={working}")

    # Run each job in its own process so we can reliably stop it.
    proc = multiprocessing.Process(target=_run_job, args=(job_id, str(store.root)), daemon=True)
    proc.start()

    # Persist PID for stop requests.
    meta = JobMetadata(**{**asdict(meta), "pid": int(proc.pid) if proc.pid else None, "updated_at": _utc_now_iso()})
    store.write_meta(meta)
    return job_id


def _stop_process(pid: int) -> None:
    if os.name == "nt":
        # /T = kill child processes, /F = force.
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            check=False,
            capture_output=True,
            text=True,
        )
        return

    # POSIX: best-effort terminate.
    try:
        os.kill(pid, 15)
    except Exception:
        pass


def get_best_scheme_txt(meta: JobMetadata) -> Optional[str]:
    p = _job_best_scheme_path(Path(meta.working_folder))
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8", errors="replace")
    return None


def get_scheme_data_csv(meta: JobMetadata) -> Optional[str]:
    analysis_dir = Path(meta.working_folder) / "analysis"
    if not analysis_dir.exists():
        return None
    # Legacy reporter writes scheme_data.csv under cfg.schemes_path. We locate it
    # defensively for compatibility across search strategies.
    for p in analysis_dir.rglob("scheme_data.csv"):
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
    return None


def list_jobs(*, limit: int = 50) -> list[JobMetadata]:
    """List known jobs from the filesystem store.

    Ordering: most recently updated first.
    """
    metas: list[JobMetadata] = []
    for job_id in store.list_job_ids():
        try:
            metas.append(store.read_meta(job_id))
        except Exception:  # noqa: BLE001
            continue

    metas.sort(key=lambda m: m.updated_at, reverse=True)
    return metas[: max(0, int(limit))]


app = FastAPI(title="PartitionFinder API", version="0.1")


@app.post("/jobs", response_model=JobSubmitResponse)
def post_jobs(req: JobRequest) -> JobSubmitResponse:
    try:
        job_id = submit_job(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JobSubmitResponse(id=job_id)


@app.get("/jobs", response_model=list[JobStatusResponse])
def get_jobs(limit: int = 50) -> list[JobStatusResponse]:
    items: list[JobStatusResponse] = []
    for meta in list_jobs(limit=limit):
        items.append(
            JobStatusResponse(
                id=meta.id,
                state=meta.state,
                created_at=meta.created_at,
                updated_at=meta.updated_at,
                datatype=meta.datatype,
                input_folder=meta.input_folder,
                cpus=_parse_cpus_from_argv(meta.argv),
                exit_code=meta.exit_code,
                error=meta.error,
            )
        )
    return items


@app.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    try:
        meta = store.read_meta(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        id=meta.id,
        state=meta.state,
        created_at=meta.created_at,
        updated_at=meta.updated_at,
        datatype=meta.datatype,
        input_folder=meta.input_folder,
        cpus=_parse_cpus_from_argv(meta.argv),
        exit_code=meta.exit_code,
        error=meta.error,
    )


@app.get("/jobs/{job_id}/results", response_model=JobResultsResponse)
def get_job_results(job_id: str) -> JobResultsResponse:
    try:
        meta = store.read_meta(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")

    analysis_path = str(Path(meta.working_folder) / "analysis")
    best_scheme_txt = get_best_scheme_txt(meta)
    scheme_data_csv = get_scheme_data_csv(meta)
    return JobResultsResponse(
        id=meta.id,
        state=meta.state,
        cpus=_parse_cpus_from_argv(meta.argv),
        best_scheme_txt=best_scheme_txt,
        scheme_data_csv=scheme_data_csv,
        analysis_path=analysis_path if Path(analysis_path).exists() else None,
    )


@app.post("/folders/preview", response_model=FolderPreviewResponse)
def post_folder_preview(req: FolderPreviewRequest) -> FolderPreviewResponse:
    """Validate a folder and extract a lightweight preview from the .cfg.

    This is UI support only; it does not run an analysis.
    """
    try:
        folder = Path(req.folder).resolve()
        _validate_input_folder(folder)
        cfg_path = _find_cfg_file(folder)
        text = cfg_path.read_text(encoding="utf-8", errors="replace")
        return FolderPreviewResponse(
            folder=str(folder),
            cfg_file=str(cfg_path),
            alignment=_parse_alignment_from_cfg(text),
            data_blocks=_parse_data_blocks_from_cfg(text),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/folders/browse", response_model=FolderBrowseResponse)
def get_folder_browse() -> FolderBrowseResponse:
    """Open a native OS folder picker and return the selected path.

    This is intentionally implemented server-side because browsers cannot
    reliably provide a real local filesystem path for a directory.
    """

    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=501,
            detail=f"Folder picker not available in this Python environment: {e}",
        )

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select PartitionFinder input folder")
        try:
            root.destroy()
        except Exception:
            pass

        folder = (folder or "").strip()
        return FolderBrowseResponse(folder=folder or None)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str) -> dict[str, str]:
    """Delete a job and all its artifacts."""
    if not store.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        meta = store.read_meta(job_id)
        if meta.state == "running":
            raise HTTPException(
                status_code=409,
                detail="Cannot delete a running job. Wait for completion or stop it first."
            )
    except KeyError:
        pass  # Metadata missing but dir exists, still allow delete
    
    deleted = store.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete job")
    
    return {"status": "deleted", "job_id": job_id}


@app.post("/jobs/{job_id}/stop", response_model=StopJobResponse)
def post_stop_job(job_id: str) -> StopJobResponse:
    """Stop a running job (best-effort).

    Implementation note: jobs run in a separate process; on Windows we use taskkill.
    """
    try:
        meta = store.read_meta(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")

    if meta.state in {"succeeded", "failed"}:
        return StopJobResponse(status="already_finished", job_id=job_id)

    if not meta.pid:
        # No PID recorded; mark failed.
        now = _utc_now_iso()
        meta2 = JobMetadata(
            **{**asdict(meta), "state": "failed", "updated_at": now, "exit_code": 1, "error": "stop requested but no pid available"}
        )
        store.write_meta(meta2)
        return StopJobResponse(status="failed", job_id=job_id)

    _stop_process(int(meta.pid))

    now = _utc_now_iso()
    meta2 = JobMetadata(
        **{
            **asdict(meta),
            "state": "failed",
            "updated_at": now,
            "exit_code": 1,
            "error": "stopped by user",
        }
    )
    store.write_meta(meta2)
    store.append_log(job_id, f"[{now}] Stopped by user")
    return StopJobResponse(status="stopped", job_id=job_id)


@app.websocket("/jobs/{job_id}/stream")
async def stream_job_logs(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()

    # Basic file tailing loop. We send any new bytes appended to job.log.
    try:
        store.read_meta(job_id)
    except KeyError:
        await websocket.send_text("Job not found")
        await websocket.close(code=1008)
        return

    log_path = store.log_path(job_id)
    offset = 0
    idle_ticks = 0

    while True:
        await asyncio.sleep(0.25)

        if log_path.exists():
            data = log_path.read_bytes()
            if offset < len(data):
                chunk = data[offset:]
                offset = len(data)
                await websocket.send_text(chunk.decode("utf-8", errors="replace"))
                idle_ticks = 0
            else:
                idle_ticks += 1
        else:
            idle_ticks += 1

        # Stop streaming shortly after completion.
        try:
            meta = store.read_meta(job_id)
        except KeyError:
            meta = None

        if meta is not None and meta.state in {"succeeded", "failed"} and idle_ticks > 8:
            await websocket.close(code=1000)
            return


def submit_and_wait(req: JobRequest, *, poll_interval_s: float = 0.5) -> JobResultsResponse:
    """Convenience for in-process callers (e.g., CLI).

    This is intentionally synchronous.
    """
    job_id = submit_job(req)
    while True:
        meta = store.read_meta(job_id)
        if meta.state in {"succeeded", "failed"}:
            break
        time.sleep(poll_interval_s)
    return JobResultsResponse(
        id=meta.id,
        state=meta.state,
        best_scheme_txt=get_best_scheme_txt(meta),
        scheme_data_csv=get_scheme_data_csv(meta),
        analysis_path=str(Path(meta.working_folder) / "analysis"),
    )
