from __future__ import annotations

import argparse
import time
from pathlib import Path

import sys


# Allow running this file directly without installing the package.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from partitionfinder.api.service import JobRequest, store, submit_job


def main() -> int:
    p = argparse.ArgumentParser(description="Smoke-test PartitionFinder API job orchestration")
    p.add_argument(
        "folder",
        nargs="?",
        default=str(Path("examples") / "nucleotide"),
        help="Input folder containing partition_finder.cfg (default: examples/nucleotide)",
    )
    p.add_argument(
        "--datatype",
        default="DNA",
        choices=["DNA", "protein", "morphology"],
        help="Datatype (default: DNA)",
    )
    p.add_argument(
        "--no-copy",
        action="store_true",
        help="Run directly in the provided folder (do not copy into job workspace)",
    )
    p.add_argument(
        "--poll",
        type=float,
        default=2.0,
        help="Polling interval in seconds (default: 2)",
    )

    args = p.parse_args()

    folder = str(Path(args.folder).resolve())
    req = JobRequest(
        folder=folder,
        datatype=args.datatype,
        args=["-f", "-n", "-p", "1"],
        copy_input=not args.no_copy,
        overrides={},
    )

    job_id = submit_job(req)
    print(f"job_id={job_id}")
    log_path = store.log_path(job_id)
    offset = 0

    while True:
        meta = store.read_meta(job_id)
        print(f"state={meta.state} updated_at={meta.updated_at} exit_code={meta.exit_code}")

        if log_path.exists():
            text = log_path.read_text(encoding="utf-8", errors="replace")
            if offset < len(text):
                print(text[offset:], end="" if text.endswith("\n") else "\n")
                offset = len(text)

        if meta.state in {"succeeded", "failed"}:
            break

        time.sleep(max(0.2, float(args.poll)))

    working = Path(meta.working_folder)
    best = working / "analysis" / "best_scheme.txt"
    print(f"working_folder={working}")
    print(f"best_scheme_exists={best.exists()}")
    if meta.error:
        print(f"error={meta.error}")

    return 0 if meta.state == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
