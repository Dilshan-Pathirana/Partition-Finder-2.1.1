from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from ._legacy_shim import import_legacy_module


def run_folder(
    folder: str | Path,
    *,
    datatype: str,
    passed_args: Optional[Iterable[str]] = None,
    name: str = "PartitionFinder",
) -> int:
    """Run an analysis for a folder using the legacy Phase 1 engine.

    This is the Phase 2 stable entrypoint that CLI/GUI/API should call.

    Args:
        folder: Folder containing partition_finder.cfg and alignment.
        datatype: One of: DNA, protein, morphology.
        passed_args: Command line args to pass through (excluding the program name).
        name: Program label.

    Returns:
        Process exit code (0 == success).
    """
    legacy_main = import_legacy_module("main")

    folder = str(Path(folder))

    # Mirror the legacy interface: main(name, datatype, passed_args)
    # The legacy parser expects a list of command-line args that contains
    # options first and ends with the folder path (no program name).
    if passed_args is None:
        argv = [folder]
    else:
        argv = [*list(passed_args), folder]

    return int(legacy_main.main(name, datatype, argv))
