# PartitionFinder 2.1.1 - Python 3 Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Modern Python 3.12+ Compatible Version**

PartitionFinder discovers optimal partitioning schemes for nucleotide, amino acid, and morphology sequence alignments. It helps find the best model of sequence evolution for phylogenetic datasets.

Originally by [Robert Lanfear et al.](http://www.robertlanfear.com/partitionfinder/)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Dilshan-Pathirana/Partition-Finder-2.1.1.git
cd Partition-Finder-2.1.1
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Usage

#### Option 1: GUI (Recommended)
Double-click `Run_PartitionFinder_GUI.bat` (Windows) or run:
```bash
python PartitionFinder_GUI.py
```

Features:
- Simple file browser interface
- Select NEXUS alignment file
- Select configuration file
- Live analysis log
- Results automatically saved to `examples/results/`

#### Option 2: Interactive Command Line
```bash
python PartitionFinder.py
```

You'll be prompted to enter:
1. Path to your NEXUS alignment file
2. Path to your configuration file (.cfg)

Results are saved to `examples/results/<filename>_results/analysis/`

#### Option 3: Direct Command Line
```bash
python PartitionFinder.py <folder_with_cfg_and_alignment>
```

---

## 📁 Input Files

### 1. NEXUS Alignment File
Your sequence alignment in NEXUS format (`.nexus` or `.nex`)

### 2. Configuration File (`partition_finder.cfg`)
Defines analysis parameters. Example:

```ini
## ALIGNMENT FILE ##
alignment = your_alignment.nexus;

## BRANCHLENGTHS: linked | unlinked ##
branchlengths = linked;

## MODELS OF EVOLUTION ##
models = JC, HKY, GTR, GTR+G, GTR+I+G;

## MODEL SELECTION: AIC | AICc | BIC ##
model_selection = aicc;

## DATA BLOCKS ##
[data_blocks]
Gene1 = 1-500;
Gene2 = 501-1000;

## SCHEMES SEARCH: greedy | rcluster | kmeans | all ##
[schemes]
search = greedy;
```

See `examples/nucleotide/partition_finder.cfg` for a complete example.

---

## 📊 Output

Results are saved in `<your_folder>/analysis/`:
- `best_scheme.txt` - Optimal partitioning scheme
- `best_models.txt` - Best-fit models for each partition
- `analysis.log` - Detailed analysis log

---

## 🧪 Example Analysis

Test with included example data:

### Using GUI:
1. Run `Run_PartitionFinder_GUI.bat`
2. Browse to `examples/nucleotide/Concatenated_SL_and_India.nexus`
3. Browse to `examples/nucleotide/partition_finder.cfg`
4. Click "Run Analysis"

### Using Command Line:
```bash
python PartitionFinder.py examples/nucleotide
```

Results will appear in `examples/nucleotide/analysis/`

---

## 🔧 Supported Analysis Types

1. **DNA Sequences** (default)
   ```bash
   python PartitionFinder.py <folder>
   ```

2. **Protein Sequences**
   ```bash
   python PartitionFinderProtein.py <folder>
   ```

3. **Morphological Data**
   ```bash
   python PartitionFinderMorphology.py <folder>
   ```

---

## 📖 Command Line Options

```bash
python PartitionFinder.py [options] <folder>

Options:
  -h, --help              Show help message
  -v, --verbose           Show debug output
  -c, --check-only        Check config files only
  -f, --force-restart     Delete previous output and restart
  -p N, --processes=N     Number of parallel processes (-1 = all CPUs)
  -r, --raxml             Use RAxML instead of PhyML
  -n, --no-ml-tree        Use NJ/MP tree instead of ML (faster)
  -q, --quick             Skip slow operations for large datasets
```

---

## 🆕 What's New in Python 3 Version

- ✅ **Python 3.8-3.12 compatible** (migrated from Python 2.7)
- ✅ **Modern GUI** with simple file selection
- ✅ **Enhanced NEXUS parser** (handles multiple formats)
- ✅ **Interactive mode** with user prompts
- ✅ **Automatic result organization** in dedicated folders
- ✅ **Better error handling** and logging
- ✅ **Cross-platform compatibility** (Windows/macOS/Linux)

---

## 📝 Requirements

Core dependencies (installed via `requirements.txt`):
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- scikit-learn >= 0.24.0
- pyparsing >= 2.4.7
- tables >= 3.6.1

---

## 🐛 Troubleshooting

### "No module named 'partfinder'"
Make sure you're running from the project root directory.

### "Failed to find configuration file"
Ensure `partition_finder.cfg` is in the same folder as your alignment.

### "No sequences found in NEXUS MATRIX block"
Your NEXUS file may have formatting issues. Check:
- File starts with `#NEXUS`
- Has a `BEGIN DATA` or `BEGIN CHARACTERS` block
- Has a `MATRIX` section with sequences

### Analysis runs but no results
Check the analysis log in `<folder>/analysis/analysis.log` for errors.

---

## 📚 Citation

If you use PartitionFinder, please cite:

```
Lanfear, R., Frandsen, P. B., Wright, A. M., Senfeld, T., & Calcott, B. (2017).
PartitionFinder 2: new methods for selecting partitioned models of evolution for molecular and morphological phylogenetic analyses.
Molecular biology and evolution, 34(3), 772-773.
```

---

## 📄 License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for full details.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Dilshan-Pathirana/Partition-Finder-2.1.1/issues)
- **Original Manual**: Available in the original PartitionFinder documentation

---

## 🙏 Acknowledgments

- Original PartitionFinder by Robert Lanfear and team
- Python 3 migration and GUI enhancements
- All contributors to the project

---

**Made with ❤️ for phylogenetics research**
