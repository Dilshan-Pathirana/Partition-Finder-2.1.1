from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

# Allow running without installing the package.
import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from partitionfinder.api.service import JobRequest, submit_and_wait  # noqa: E402


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    folder: str
    datatype: str
    args: list[str]


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    folder: str
    datatype: str
    args: list[str]
    state: str
    seconds: float


DEFAULT_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        name="nucleotide",
        folder=str(Path("examples") / "nucleotide"),
        datatype="DNA",
        args=["-f", "-n", "-p", "1"],
    ),
    BenchmarkCase(
        name="aminoacid",
        folder=str(Path("examples") / "aminoacid"),
        datatype="protein",
        args=["-f", "-n", "-p", "1"],
    ),
    BenchmarkCase(
        name="morphology",
        folder=str(Path("examples") / "morphology"),
        datatype="morphology",
        args=["-f", "-n", "-p", "1", "--raxml"],
    ),
]


def run_case(case: BenchmarkCase, *, copy_input: bool) -> BenchmarkResult:
    t0 = time.perf_counter()
    result = submit_and_wait(
        JobRequest(
            folder=str(Path(case.folder).resolve()),
            datatype=case.datatype,  # type: ignore[arg-type]
            args=list(case.args),
            copy_input=copy_input,
            overrides={},
        ),
        poll_interval_s=0.5,
    )
    dt = time.perf_counter() - t0
    return BenchmarkResult(
        name=case.name,
        folder=str(Path(case.folder)),
        datatype=case.datatype,
        args=list(case.args),
        state=result.state,
        seconds=float(dt),
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Benchmark PartitionFinder example datasets")
    p.add_argument(
        "--out",
        default=str(Path(".pf_bench") / "bench.json"),
        help="Output JSON path (default: .pf_bench/bench.json)",
    )
    p.add_argument(
        "--no-copy",
        action="store_true",
        help="Run directly in example folders (default copies into job workspace)",
    )

    args = p.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[BenchmarkResult] = []
    for case in DEFAULT_CASES:
        print(f"== {case.name} ==")
        r = run_case(case, copy_input=not args.no_copy)
        results.append(r)
        print(f"state={r.state} seconds={r.seconds:.2f}")

    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": [asdict(r) for r in results],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

    # Non-zero if any failed.
    return 0 if all(r.state == "succeeded" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
