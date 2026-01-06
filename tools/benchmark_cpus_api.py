"""Benchmark opt-in API CPU parallelism.

Runs PartitionFinder via the FastAPI service layer (in-process):
JobRequest -> submit_and_wait -> legacy engine.

This simulates what the React UI does (POST /jobs) while remaining simple to run.

Outputs:
- Wall-time per cpus setting
- Sanity check that best_scheme results match baseline cpus=1 within tolerances

Usage:
  python tools/benchmark_cpus_api.py examples/nucleotide --datatype DNA --cpus 1 4 8

Notes:
- For reproducibility guardrails, this always uses copy_input=True.
- It avoids writing into the repo-wide .pf_jobs/ by using a private JobStore
  under .pf_bench/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def _normalize_model(model_text: str) -> str:
    model_text = model_text.strip()
    if model_text.startswith("b'") and model_text.endswith("'"):
        return model_text[2:-1]
    if model_text.startswith('b"') and model_text.endswith('"'):
        return model_text[2:-1]
    return model_text


def _parse_best_scheme_text(txt: str) -> dict:
    def grab(pattern: str) -> str:
        m = re.search(pattern, txt, flags=re.MULTILINE)
        if not m:
            raise RuntimeError(f"Failed to parse {pattern!r} from best_scheme text")
        return m.group(1).strip()

    scheme_name = grab(r"^Scheme Name\s*:\s*(\S+)")
    lnl = float(grab(r"^Scheme lnL\s*:\s*([-0-9.eE]+)"))

    criterion_value = None
    criterion = None
    if re.search(r"^Scheme AICc\s*:\s*", txt, flags=re.MULTILINE):
        criterion = "aicc"
        criterion_value = float(grab(r"^Scheme AICc\s*:\s*([-0-9.eE]+)"))
    elif re.search(r"^Scheme AIC\s*:\s*", txt, flags=re.MULTILINE):
        criterion = "aic"
        criterion_value = float(grab(r"^Scheme AIC\s*:\s*([-0-9.eE]+)"))
    elif re.search(r"^Scheme BIC\s*:\s*", txt, flags=re.MULTILINE):
        criterion = "bic"
        criterion_value = float(grab(r"^Scheme BIC\s*:\s*([-0-9.eE]+)"))
    else:
        raise RuntimeError("No Scheme AIC/AICc/BIC line found")

    num_subsets = int(grab(r"^Number of subsets\s*:\s*(\d+)"))

    subset_models: list[str] = []
    for line in txt.splitlines():
        m = re.match(r"^\s*\d+\s*\|\s*(.*?)\s*\|", line)
        if m:
            subset_models.append(_normalize_model(m.group(1)))

    if not subset_models:
        raise RuntimeError("No subset model lines parsed")

    return {
        "scheme_name": scheme_name,
        "lnl": lnl,
        "criterion": criterion,
        "criterion_value": float(criterion_value),
        "num_subsets": num_subsets,
        "subset_best_models": subset_models,
    }


def _approx_equal(a: float, b: float, *, abs_tol: float) -> bool:
    return abs(a - b) <= abs_tol


def _copy_input_folder(src: Path, dst: Path) -> Path:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    # Normalize config naming.
    cfg = dst / "partition_finder.cfg"
    if not cfg.exists():
        candidates = list(dst.glob("*.cfg"))
        if len(candidates) == 1:
            shutil.copy2(candidates[0], cfg)
        elif len(candidates) > 1:
            raise RuntimeError(f"Multiple .cfg files in {dst}, cannot infer which to use")
        else:
            raise RuntimeError(f"No .cfg found in {dst}")

    return dst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default="examples/nucleotide")
    ap.add_argument("--datatype", choices=["DNA", "protein", "morphology"], default="DNA")
    ap.add_argument("--cpus", nargs="+", type=int, default=[1, 4, 8])
    ap.add_argument("--out", default=".pf_bench/cpus_bench_api.json")
    args = ap.parse_args()

    folder = (REPO_ROOT / args.folder).resolve() if not Path(args.folder).is_absolute() else Path(args.folder).resolve()
    if not folder.exists():
        raise SystemExit(f"Folder not found: {folder}")

    # Stabilize BLAS/NumExpr threads (separate from PF's -p concurrency).
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

    from partitionfinder.api import service as svc

    bench_root = (REPO_ROOT / ".pf_bench" / f"cpus_api_{int(time.time())}").resolve()
    bench_root.mkdir(parents=True, exist_ok=True)

    # Ensure we don't pollute the repo-wide job store.
    svc.store = svc.JobStore(bench_root / "jobs")

    runs = []
    baseline_parsed = None

    for cpus in args.cpus:
        # Always isolate input for safety when cpus>1.
        work_dir = _copy_input_folder(folder, bench_root / f"work_{folder.name}_cpus{cpus}")

        # Preserve legacy baseline flags, but omit -p so the API layer can inject it.
        legacy_args = ["-f", "-n"]
        if args.datatype == "morphology":
            legacy_args.append("--raxml")

        req = svc.JobRequest(
            folder=str(work_dir),
            datatype=args.datatype,
            cpus=int(cpus),
            args=legacy_args,
            copy_input=True,
        )

        t0 = time.perf_counter()
        res = svc.submit_and_wait(req, poll_interval_s=0.5)
        dt = time.perf_counter() - t0

        if res.state != "succeeded":
            raise RuntimeError(f"Run failed for cpus={cpus} (state={res.state}).")
        if not res.best_scheme_txt:
            raise RuntimeError(f"Missing best_scheme_txt for cpus={cpus}.")

        parsed = _parse_best_scheme_text(res.best_scheme_txt)
        if baseline_parsed is None and int(cpus) == 1:
            baseline_parsed = parsed
        elif baseline_parsed is not None:
            # Compare key outputs. Tolerances match tests.
            if parsed["scheme_name"] != baseline_parsed["scheme_name"]:
                raise RuntimeError(f"Scheme name differs at cpus={cpus}: {parsed['scheme_name']} vs {baseline_parsed['scheme_name']}")
            if parsed["criterion"] != baseline_parsed["criterion"]:
                raise RuntimeError(f"Criterion differs at cpus={cpus}: {parsed['criterion']} vs {baseline_parsed['criterion']}")
            if parsed["num_subsets"] != baseline_parsed["num_subsets"]:
                raise RuntimeError(f"Num subsets differs at cpus={cpus}: {parsed['num_subsets']} vs {baseline_parsed['num_subsets']}")
            if parsed["subset_best_models"] != baseline_parsed["subset_best_models"]:
                raise RuntimeError(
                    f"Best models differ at cpus={cpus}: {parsed['subset_best_models']} vs {baseline_parsed['subset_best_models']}"
                )
            if not _approx_equal(parsed["lnl"], baseline_parsed["lnl"], abs_tol=1e-6):
                raise RuntimeError(f"lnL differs at cpus={cpus}: {parsed['lnl']} vs {baseline_parsed['lnl']}")
            if not _approx_equal(parsed["criterion_value"], baseline_parsed["criterion_value"], abs_tol=1e-3):
                raise RuntimeError(
                    f"Criterion value differs at cpus={cpus}: {parsed['criterion_value']} vs {baseline_parsed['criterion_value']}"
                )

        runs.append(
            {
                "cpus": int(cpus),
                "seconds": dt,
                "scheme_name": parsed["scheme_name"],
                "criterion": parsed["criterion"],
                "criterion_value": parsed["criterion_value"],
                "lnl": parsed["lnl"],
                "num_subsets": parsed["num_subsets"],
            }
        )

    out_path = (REPO_ROOT / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"folder": str(folder), "datatype": args.datatype, "runs": runs}, indent=2), encoding="utf-8")

    # Print a compact summary.
    best = min(runs, key=lambda r: r["seconds"]) if runs else None
    print("\nCPU benchmark via API")
    for r in runs:
        print(f"  cpus={r['cpus']:>2}  seconds={r['seconds']:.2f}")
    if best:
        print(f"Best: cpus={best['cpus']} seconds={best['seconds']:.2f}")
    print(f"Wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
