from __future__ import annotations

import os
from typing import Literal


Backend = Literal["rust", "python"]


def _try_import_rust():
    try:
        # Built by maturin as a Python extension module.
        # We keep the import local so this file is always importable.
        from . import _pf_accel as rust_mod  # type: ignore

        return rust_mod
    except Exception:
        return None


_RUST = _try_import_rust()


def _env_backend_override() -> Backend | None:
    v = os.environ.get("PF_ACCEL", "").strip().lower()
    if not v:
        return None
    if v in {"0", "false", "off", "no", "python"}:
        return "python"
    if v in {"1", "true", "on", "yes", "rust"}:
        return "rust"
    # Unknown value -> ignore (keep default behavior).
    return None


def backend() -> Backend:
    override = _env_backend_override()
    if override == "python":
        return "python"
    if override == "rust":
        return "rust" if _RUST is not None else "python"
    return "rust" if _RUST is not None else "python"


def add_i64(a: int, b: int) -> int:
    """Tiny example function used to validate the Rust/Python fallback wiring.

    This is intentionally simple so it can't affect scientific results.
    Real accelerated functions will be added behind the same wrapper pattern.
    """

    if _RUST is not None:
        return int(_RUST.add_i64(int(a), int(b)))
    return int(a) + int(b)


def subset_list_stats(
    best_params: list[float],
    best_lnl: list[float],
    subset_sizes: list[int],
    *,
    num_taxa: int,
    branchlengths: str,
) -> tuple[float, int, int]:
    """Compute (lnL, sum_k, subs_len) for a list of subsets.

    This is performance-sensitive when many schemes are evaluated.

    Args mirror the legacy `subset_ops.subset_list_stats` logic.

    When the Rust extension is available, we call it. Otherwise we compute in
    pure Python.
    """

    if not (len(best_params) == len(best_lnl) == len(subset_sizes)):
        raise ValueError("best_params, best_lnl, subset_sizes must have same length")

    if _RUST is not None:
        lnL, sum_k, subs_len = _RUST.subset_list_stats(
            best_params,
            best_lnl,
            subset_sizes,
            int(num_taxa),
            str(branchlengths),
        )
        return float(lnL), int(sum_k), int(subs_len)

    sum_subset_k = 0.0
    lnL = 0.0
    subs_len = 0
    for k, lnl, nsites in zip(best_params, best_lnl, subset_sizes):
        sum_subset_k += float(k)
        lnL += float(lnl)
        subs_len += int(nsites)

    if branchlengths == "linked":
        sum_k = int(sum_subset_k + (len(best_params) - 1) + ((2 * int(num_taxa)) - 3))
    elif branchlengths == "unlinked":
        sum_k = int(sum_subset_k + (len(best_params) * ((2 * int(num_taxa)) - 3)))
    else:
        raise ValueError(f"Unknown branchlengths: {branchlengths!r}")

    return lnL, sum_k, subs_len


def subset_list_score(
    best_params: list[float],
    best_lnl: list[float],
    subset_sizes: list[int],
    *,
    num_taxa: int,
    branchlengths: str,
    model_selection: str,
) -> float:
    """Compute AIC/AICc/BIC score for a list of subsets.

    This bundles the stats + scoring in one call so the Rust backend can avoid
    extra Python overhead.
    """

    if _RUST is not None:
        override = _env_backend_override()
        if override != "python":
            return float(
                _RUST.subset_list_score(
                    best_params,
                    best_lnl,
                    subset_sizes,
                    int(num_taxa),
                    str(branchlengths),
                    str(model_selection),
                )
            )

    lnL, sum_k, subs_len = subset_list_stats(
        best_params,
        best_lnl,
        subset_sizes,
        num_taxa=num_taxa,
        branchlengths=branchlengths,
    )

    ms = str(model_selection).lower()
    if ms == "aic":
        return (-2.0 * float(lnL)) + (2.0 * float(sum_k))
    if ms == "aicc":
        n = float(subs_len)
        k = float(sum_k)
        if n < (k + 2.0):
            n = k + 2.0
        return (-2.0 * float(lnL)) + ((2.0 * k) * (n / (n - k - 1.0)))
    if ms == "bic":
        n = float(subs_len)
        k = float(sum_k)
        # log(n) without importing math on this hot path; use Python's float method.
        import math

        return (-2.0 * float(lnL)) + (k * math.log(n))

    raise ValueError(f"Unknown model_selection: {model_selection!r}")
