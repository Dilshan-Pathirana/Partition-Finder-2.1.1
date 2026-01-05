"""Partition scheme generation.

Phase 2 API wrapper: stable import location for scheme-related objects.

Implementation note:
- Currently re-exports the Phase 1 legacy engine types.
"""

from __future__ import annotations

from ._legacy_shim import import_legacy_module

_legacy_scheme = import_legacy_module("scheme")

SchemeError = _legacy_scheme.SchemeError
SchemeResult = _legacy_scheme.SchemeResult
Scheme = _legacy_scheme.Scheme
SchemeSet = _legacy_scheme.SchemeSet
