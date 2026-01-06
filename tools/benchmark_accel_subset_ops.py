from __future__ import annotations

import argparse
import time
from pathlib import Path

# Allow running without installing the package.
import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main() -> int:
    p = argparse.ArgumentParser(description="Micro-benchmark accel subset ops helpers")
    p.add_argument("--n", type=int, default=2_000_000, help="Iterations (default: 2,000,000)")
    args = p.parse_args()

    from partitionfinder.accel import backend, subset_list_score, subset_list_stats

    best_params = [1.0, 2.0, 5.0, 3.0]
    best_lnl = [-10.0, -20.5, -3.25, -9.0]
    subset_sizes = [100, 50, 25, 10]

    print(f"backend={backend()}")

    # Warm up
    subset_list_stats(best_params, best_lnl, subset_sizes, num_taxa=18, branchlengths="linked")
    subset_list_score(
        best_params,
        best_lnl,
        subset_sizes,
        num_taxa=18,
        branchlengths="linked",
        model_selection="aicc",
    )

    t0 = time.perf_counter()
    acc = 0.0
    for _ in range(args.n):
        lnL, sum_k, subs_len = subset_list_stats(
            best_params,
            best_lnl,
            subset_sizes,
            num_taxa=18,
            branchlengths="linked",
        )
        acc += lnL + sum_k + subs_len
    dt_stats = time.perf_counter() - t0

    t1 = time.perf_counter()
    acc2 = 0.0
    for _ in range(args.n):
        acc2 += subset_list_score(
            best_params,
            best_lnl,
            subset_sizes,
            num_taxa=18,
            branchlengths="linked",
            model_selection="aicc",
        )
    dt_score = time.perf_counter() - t1

    print(f"stats_seconds={dt_stats:.3f} stats_per_sec={args.n / dt_stats:,.0f}")
    print(f"score_seconds={dt_score:.3f} score_per_sec={args.n / dt_score:,.0f}")
    # prevent dead-code elimination
    print(f"acc={acc:.3f} acc2={acc2:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
