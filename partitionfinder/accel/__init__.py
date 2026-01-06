"""Optional native acceleration layer (Phase 4).

This package is *always* safe to import. If the Rust extension is not built
(or Rust isn't installed), we fall back to pure-Python implementations.

The goal is to isolate performance work without changing scientific results.
"""

from __future__ import annotations

from ._api import add_i64, backend, subset_list_score, subset_list_stats

__all__ = ["add_i64", "backend", "subset_list_score", "subset_list_stats"]
