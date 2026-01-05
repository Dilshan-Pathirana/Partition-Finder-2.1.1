# Python2 ↔ Python3 Baseline Comparison (Phase 1)

Phase 1 requires numerical equivalence verification against the original PartitionFinder 2 (Python 2) baseline.

This repo is the **Python 3 Edition** baseline. The goal is to demonstrate that, for the bundled example datasets, the Python 3 results match the Python 2 results, allowing only floating-point tolerance.

## What to compare

PartitionFinder writes canonical summaries here:

- `<run_folder>/analysis/best_scheme.txt`

This file includes:

- Best scheme name
- Best model per subset
- Score for the selected criterion (AIC / AICc / BIC)
- lnL

## How to run the Python 3 baseline (this repo)

From the repo root:

- DNA: `python PartitionFinder.py -f -n -p 1 <folder>`
- Protein: `python PartitionFinderProtein.py -f -n -p 1 <folder>`
- Morphology: `python PartitionFinderMorphology.py -f -n -p 1 --raxml <folder>`

Example folders:

- `examples/nucleotide`
- `examples/aminoacid`
- `examples/morphology`

## How to run the Python 2 baseline

1. Obtain the upstream PartitionFinder 2 (Python 2.7) release.
2. Create a clean Python 2 environment (e.g., conda) and install PF2’s dependencies.
3. Run the same example folders and capture the output `analysis/best_scheme.txt`.

Notes:

- Use the same external phylogeny program where applicable (PhyML vs RAxML).
- For morphology, PF2 uses RAxML.
- Use `-p 1` to reduce nondeterminism.

## Automated comparison helper

This repo includes a small comparator:

- [tools/compare_baselines.py](tools/compare_baselines.py)

Usage:

- `python tools/compare_baselines.py --py2 <path_to_py2_best_scheme.txt> --py3 <path_to_py3_best_scheme.txt>`

It will exit with:

- `0` if all values match (within tolerances)
- `2` if any differences are detected

You can adjust tolerances:

- `--abs-tol 1e-3` (score tolerance)
- `--lnl-abs-tol 1e-6` (lnL tolerance)

## Recording deviations

If differences appear:

- Record the dataset and exact differences.
- Note the likely cause (dependency versions, external program version, platform-specific floating-point behavior).
- Explain why the difference is scientifically acceptable (if it is) — otherwise treat as a regression.

This document should be updated with any confirmed deviations before tagging the immutable Phase 1 baseline.
