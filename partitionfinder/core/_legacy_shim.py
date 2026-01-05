from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType


def legacy_root() -> Path:
    """Return the directory that contains the Phase 1 legacy engine modules."""
    return Path(__file__).resolve().parent / "_legacy_partfinder"


def ensure_legacy_on_syspath() -> None:
    """Make legacy modules importable by their historical top-level names.

    The Phase 1 engine uses absolute imports like `import util`, `import logtools`.
    To preserve behavior without rewriting legacy imports (yet), we temporarily
    add the legacy module directory to `sys.path`.
    """
    legacy = str(legacy_root())
    if legacy not in sys.path:
        sys.path.insert(0, legacy)


def import_legacy_module(module_name: str) -> ModuleType:
    """Import a legacy module by its historical name (e.g., 'alignment')."""
    ensure_legacy_on_syspath()
    return importlib.import_module(module_name)
