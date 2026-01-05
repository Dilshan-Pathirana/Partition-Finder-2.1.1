"""Core execution API for PartitionFinder.

All scientific execution must be invokable programmatically via this package.
"""

from .alignment import AlignmentError, AlignmentParser, make_alignment_parser  # noqa: F401
from .runners import run_folder  # noqa: F401
from .schemes import Scheme, SchemeError, SchemeResult, SchemeSet  # noqa: F401
from .scoring import ExternalProgramError, PartitionFinderError, get_aic, get_aicc, get_bic  # noqa: F401
