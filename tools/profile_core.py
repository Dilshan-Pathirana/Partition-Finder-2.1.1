from __future__ import annotations

import argparse
import cProfile
import shutil
import time
from pathlib import Path

# Allow running without installing the package.
import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from partitionfinder.core import run_folder  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Profile core run_folder() with cProfile")
    p.add_argument(
        "folder",
        nargs="?",
        default=str(Path("examples") / "aminoacid"),
        help="Input folder containing partition_finder.cfg (default: examples/aminoacid)",
    )
    p.add_argument(
        "--datatype",
        default="protein",
        choices=["DNA", "protein", "morphology"],
        help="Datatype (default: protein)",
    )
    p.add_argument(
        "--out",
        default=str(Path(".pf_bench") / "profile_core.prof"),
        help="Profiler output path (default: .pf_bench/profile_core.prof)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=50,
        help="Number of top lines to print (default: 50)",
    )
    p.add_argument(
        "--no-copy",
        action="store_true",
        help="Run directly in the provided folder (default copies to a temp work dir)",
    )

    args = p.parse_args()

    src = Path(args.folder).resolve()
    if not src.exists() or not src.is_dir():
        raise SystemExit(f"Folder not found: {src}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.no_copy:
        work = src
    else:
        # Copy to a dedicated profiling work dir so we don't mutate examples.
        work = Path(".pf_bench") / f"profile_work_{src.name}"
        if work.exists():
            shutil.rmtree(work)
        shutil.copytree(src, work)

    pr = cProfile.Profile()
    t0 = time.perf_counter()
    pr.enable()
    exit_code = run_folder(str(work), datatype=args.datatype, passed_args=["-f", "-n", "-p", "1"], name="PartitionFinder")
    pr.disable()
    dt = time.perf_counter() - t0

    pr.dump_stats(str(out_path))
    print(f"exit_code={exit_code} seconds={dt:.2f}")
    print(f"wrote={out_path}")

    import pstats

    pstats.Stats(pr).strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE).print_stats(args.top)

    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
