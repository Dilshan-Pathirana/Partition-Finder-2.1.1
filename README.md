# PartitionFinder 2 - Python 3 Edition

A modernized version of PartitionFinder 2 for Python 3.8+, rebuilt from the original Python 2.7 codebase.

## About

PartitionFinder 2 is a tool for simultaneously selecting partitioning schemes and models of molecular evolution for phylogenetic analyses of DNA, protein, and morphological data.

**This Version:**
- ✅ Full Python 3.8+ compatibility (30+ fixes from Python 2.7)
- ✅ Updated dependencies (numpy, pandas, scipy, scikit-learn)
- ✅ Cross-platform support (Windows, Mac, Linux)
- ✅ All scientific algorithms unchanged from original

## Quick Start

### Installation

**Windows:**
```bash
py -3.12 -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip install -r requirements.txt
```

### Quick Test

**Windows:**
```bash
py -3.12 PartitionFinder.py examples/nucleotide
```

**Mac/Linux:**
```bash
python3 PartitionFinder.py examples/nucleotide
```

Results appear in `examples/nucleotide/analysis/best_scheme.txt`

## Complete Documentation

📖 **See [HOW_TO_RUN.md](HOW_TO_RUN.md) for complete installation and usage instructions.**

## Requirements

- Python 3.8 or higher (tested on 3.12)
- Dependencies: numpy, pandas, pytables, pyparsing, scipy, scikit-learn

## Usage

**For DNA/Nucleotide data:**

*Windows:* `py -3.12 PartitionFinder.py <folder_with_config>`  
*Mac/Linux:* `python3 PartitionFinder.py <folder_with_config>`

**For Protein data:**

*Windows:* `py -3.12 PartitionFinderProtein.py <folder_with_config>`  
*Mac/Linux:* `python3 PartitionFinderProtein.py <folder_with_config>`

**For Morphological data:**

*Windows:* `py -3.12 PartitionFinderMorphology.py <folder_with_config> --raxml`  
*Mac/Linux:* `python3 PartitionFinderMorphology.py <folder_with_config> --raxml`

## Citation

If you use PartitionFinder in your research, please cite:

> Lanfear, R., Frandsen, P. B., Wright, A. M., Senfeld, T., Calcott, B. (2016)  
> PartitionFinder 2: new methods for selecting partitioned models of evolution for molecular and morphological phylogenetic analyses.  
> Molecular Biology and Evolution. DOI: 10.1093/molbev/msw260

## About This Version

**Original Software:** PartitionFinder 2 by Lanfear et al. (2016)  
**This Modernization:** Python 3 migration and compatibility fixes (December 2025)

> ⚠️ **Important:** This is an independent Python 3 port and is NOT affiliated with or endorsed by the original PartitionFinder team. All scientific algorithms remain unchanged from the original version.

### What Was Fixed

- Python 2 → 3 syntax (print, xrange, iteritems, etc.)
- Updated deprecated modules (imp → importlib, time.clock → time.perf_counter)
- Fixed bytes/string encoding issues
- Updated numpy/scipy deprecated functions
- Fixed scikit-learn KMeans compatibility
- Resolved integer division issues
- All file I/O mode corrections

## License

This software is licensed under GPL v3. See LICENSE file for details.

---

**Version:** 2.1.1-py3  
**Release Date:** December 2025  
**Platform Support:** Windows, macOS, Linux
