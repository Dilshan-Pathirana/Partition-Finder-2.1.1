"""Alignment parsing and validation.

Phase 2 API wrapper: this module provides a stable import location for
alignment-related functionality.

Implementation note:
- For now, this delegates to the Phase 1 legacy engine to preserve scientific
  behavior and file format handling.
"""

from __future__ import annotations

from typing import Any

from ._legacy_shim import import_legacy_module

_legacy_alignment = import_legacy_module("alignment")

AlignmentError = _legacy_alignment.AlignmentError
AlignmentParser = _legacy_alignment.AlignmentParser

valid_nucleotide = _legacy_alignment.valid_nucleotide
valid_amino = _legacy_alignment.valid_amino
valid_morph = _legacy_alignment.valid_morph


def make_alignment_parser(stream: Any, *, datatype: str) -> AlignmentParser:
    """Create a legacy alignment parser for a given datatype.

    Args:
        stream: File-like object.
        datatype: 'DNA', 'protein', or 'morphology'.

    Returns:
        An `AlignmentParser` instance configured for the datatype.
    """
    datatype_norm = datatype.lower()
    if datatype_norm == "dna":
        valid_bases = valid_nucleotide
    elif datatype_norm == "protein":
        valid_bases = valid_amino
    elif datatype_norm in {"morphology", "morph"}:
        valid_bases = valid_morph
    else:
        raise ValueError(f"Unsupported datatype: {datatype!r}")

    return AlignmentParser(stream, valid_bases=valid_bases)
