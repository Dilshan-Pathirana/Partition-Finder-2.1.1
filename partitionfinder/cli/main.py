from __future__ import annotations

import argparse
import sys
from typing import Iterable, Optional

from partitionfinder.api.service import JobRequest, submit_and_wait


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="partitionfinder",
        description="PartitionFinder (Phase 2 CLI wrapper over partitionfinder.core)",
    )
    parser.add_argument(
        "--datatype",
        default="DNA",
        choices=["DNA", "protein", "morphology"],
        help="Datatype for the analysis.",
    )
    parser.add_argument(
        "folder",
        help="Folder containing partition_finder.cfg and the alignment.",
    )

    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Run directly in the provided folder (do not copy into job workspace).",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    known, passthrough = parser.parse_known_args(list(argv))

    # Phase 2.2: run via API job orchestration layer.
    # Pass all unknown args through to the legacy engine (e.g., -p/-n/--raxml).
    req = JobRequest(
        folder=known.folder,
        datatype=known.datatype,
        args=list(passthrough),
        copy_input=not bool(known.no_copy),
    )
    result = submit_and_wait(req)
    return 0 if result.state == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
