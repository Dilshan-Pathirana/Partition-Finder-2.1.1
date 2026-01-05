"""Model scoring and selection helpers.

Phase 2 API wrapper: stable import location for scoring functions.

Implementation note:
- Currently delegates to legacy helpers to preserve numerical behavior.
"""

from __future__ import annotations

from ._legacy_shim import import_legacy_module

_legacy_util = import_legacy_module("util")

PartitionFinderError = _legacy_util.PartitionFinderError
ExternalProgramError = _legacy_util.ExternalProgramError

get_aic = _legacy_util.get_aic
get_aicc = _legacy_util.get_aicc
get_bic = _legacy_util.get_bic
