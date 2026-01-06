from __future__ import annotations

import argparse
import cProfile
import pstats
import time
from pathlib import Path

# Allow running without installing the package.
import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from partitionfinder.api.service import JobRequest, submit_and_wait  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Profile a PartitionFinder run with cProfile")
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
        "--out",
        default=str(Path(".pf_bench") / "profile.prof"),
        help="Profiler output path (default: .pf_bench/profile.prof)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=40,
        help="Number of top lines to print (default: 40)",
    )

    args = p.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    folder = str(Path(args.folder).resolve())

    req = JobRequest(
        folder=folder,
        datatype=args.datatype,  # type: ignore[arg-type]
        args=["-f", "-n", "-p", "1"],
        copy_input=True,
        overrides={},
    )

    pr = cProfile.Profile()
    t0 = time.perf_counter()
    pr.enable()
    result = submit_and_wait(req, poll_interval_s=0.5)
    pr.disable()
    dt = time.perf_counter() - t0

    pr.dump_stats(str(out_path))
    print(f"state={result.state} seconds={dt:.2f}")
    print(f"wrote={out_path}")

    s = pstats.Stats(pr).strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE)
    s.print_stats(args.top)

    return 0 if result.state == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
