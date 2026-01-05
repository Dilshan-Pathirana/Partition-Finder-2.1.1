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
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel, Field

from partitionfinder.core import run_folder


JobState = Literal["queued", "running", "succeeded", "failed"]


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
    exit_code: Optional[int] = None
    error: Optional[str] = None
    progress_pct: Optional[float] = None  # For future enhancement


class JobRequest(BaseModel):
    folder: str = Field(..., description="Path to folder containing partition_finder.cfg")
    datatype: Literal["DNA", "protein", "morphology"] = "DNA"
    args: list[str] = Field(default_factory=list, description="Legacy CLI args (e.g., ['-p','1','-n','-f'])")
    copy_input: bool = Field(
        default=True,
        description="If true, copy the input folder into an isolated job working dir.",
    )


class JobSubmitResponse(BaseModel):
    id: str


class JobStatusResponse(BaseModel):
    id: str
    state: JobState
    created_at: str
    updated_at: str
    datatype: str | None = None
    input_folder: str | None = None
    exit_code: Optional[int] = None
    error: Optional[str] = None


class JobResultsResponse(BaseModel):
    id: str
    state: JobState
    best_scheme_txt: Optional[str] = None
    analysis_path: Optional[str] = None


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
        with self._lock:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(asdict(meta), indent=2), encoding="utf-8")

    def read_meta(self, job_id: str) -> JobMetadata:
        p = self.meta_path(job_id)
        if not p.exists():
            raise KeyError(job_id)
        raw = json.loads(p.read_text(encoding="utf-8"))
        return JobMetadata(**raw)

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


def _run_job(job_id: str) -> None:
    meta = store.read_meta(job_id)

    # Capture Python logging output (including legacy engine logs) into the
    # per-job log file so WS streaming shows meaningful progress.
    file_handler = logging.FileHandler(store.log_path(job_id), mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(levelname)-8s | %(asctime)s | %(name)-10s | %(message)s")
    )

    root_logger = logging.getLogger("")
    root_logger.addHandler(file_handler)

    store.append_log(job_id, f"[{_utc_now_iso()}] Starting job {job_id}")

    try:
        now = _utc_now_iso()
        meta = JobMetadata(
            **{**asdict(meta), "state": "running", "updated_at": now}
        )
        store.write_meta(meta)

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
        store.write_meta(meta)
        store.append_log(job_id, f"[{_utc_now_iso()}] Finished with exit_code={exit_code}")

    except Exception as e:  # noqa: BLE001
        now = _utc_now_iso()
        store.append_log(job_id, f"[{now}] ERROR: {e!r}")
        meta = JobMetadata(
            **{
                **asdict(meta),
                "state": "failed",
                "updated_at": now,
                "exit_code": 1,
                "error": repr(e),
            }
        )
        store.write_meta(meta)

    finally:
        root_logger.removeHandler(file_handler)
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

    now = _utc_now_iso()
    meta = JobMetadata(
        id=job_id,
        created_at=now,
        updated_at=now,
        state="queued",
        datatype=req.datatype,
        input_folder=str(src),
        working_folder=str(working),
        argv=list(req.args),
    )
    store.write_meta(meta)
    store.append_log(job_id, f"[{now}] Queued job; working_folder={working}")

    t = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    t.start()
    return job_id


def get_best_scheme_txt(meta: JobMetadata) -> Optional[str]:
    p = _job_best_scheme_path(Path(meta.working_folder))
    if p.exists() and p.is_file():
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
    return JobResultsResponse(
        id=meta.id,
        state=meta.state,
        best_scheme_txt=best_scheme_txt,
        analysis_path=analysis_path if Path(analysis_path).exists() else None,
    )


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
        analysis_path=str(Path(meta.working_folder) / "analysis"),
    )
