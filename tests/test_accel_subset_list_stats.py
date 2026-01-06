from __future__ import annotations

import pytest


def _py_reference(best_params: list[float], best_lnl: list[float], subset_sizes: list[int], *, num_taxa: int, branchlengths: str):
    if not (len(best_params) == len(best_lnl) == len(subset_sizes)):
        raise ValueError

    lnL = float(sum(best_lnl))
    sum_subset_k = float(sum(best_params))
    subs_len = int(sum(subset_sizes))

    if branchlengths == "linked":
        sum_k = int(sum_subset_k + (len(best_params) - 1) + ((2 * int(num_taxa)) - 3))
    elif branchlengths == "unlinked":
        sum_k = int(sum_subset_k + (len(best_params) * ((2 * int(num_taxa)) - 3)))
    else:
        raise ValueError

    return lnL, sum_k, subs_len


def test_subset_list_stats_matches_reference_when_rust_available():
    from partitionfinder.accel import backend, subset_list_score, subset_list_stats

    if backend() != "rust":
        pytest.skip("Rust extension not installed")

    best_params = [1.0, 2.0, 5.0]
    best_lnl = [-10.0, -20.5, -3.25]
    subset_sizes = [100, 50, 25]

    for branchlengths in ["linked", "unlinked"]:
        got = subset_list_stats(
            best_params,
            best_lnl,
            subset_sizes,
            num_taxa=18,
            branchlengths=branchlengths,
        )
        exp = _py_reference(best_params, best_lnl, subset_sizes, num_taxa=18, branchlengths=branchlengths)
        assert got == exp

        for model_selection in ["aic", "aicc", "bic"]:
            got_score = subset_list_score(
                best_params,
                best_lnl,
                subset_sizes,
                num_taxa=18,
                branchlengths=branchlengths,
                model_selection=model_selection,
            )
            # compute score from reference outputs
            lnl, sum_k, subs_len = exp
            if model_selection == "aic":
                exp_score = (-2.0 * lnl) + (2.0 * float(sum_k))
            elif model_selection == "aicc":
                n = float(subs_len)
                k = float(sum_k)
                if n < (k + 2.0):
                    n = k + 2.0
                exp_score = (-2.0 * lnl) + ((2.0 * k) * (n / (n - k - 1.0)))
            else:
                import math

                exp_score = (-2.0 * lnl) + (float(sum_k) * math.log(float(subs_len)))

            assert got_score == exp_score


def test_subset_list_score_python_fallback_always_available():
    from partitionfinder.accel import subset_list_score

    best_params = [1.0, 2.0]
    best_lnl = [-10.0, -2.0]
    subset_sizes = [10, 5]

    # Should always run (even without Rust installed).
    v = subset_list_score(
        best_params,
        best_lnl,
        subset_sizes,
        num_taxa=4,
        branchlengths="linked",
        model_selection="aicc",
    )
    assert isinstance(v, float)
