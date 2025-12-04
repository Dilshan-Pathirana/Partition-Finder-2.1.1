# PartitionFinder 2 - Python 3 Edition 🧬

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/)

**Modern Python 3 port with standalone GUI** | Originally by [Robert Lanfear et al.](http://www.robertlanfear.com/partitionfinder/)

A tool for selecting best-fit partitioning schemes and models of molecular evolution for phylogenetic analyses of DNA, protein, and morphological data.

![GUI Screenshot](docs/gui-screenshot.png)

---

## 🚀 Quick Start

### Option 1: Standalone Executable (Windows - No Python Needed!)

**Perfect for non-technical users:**

1. **Download**: [`PartitionFinder-2.1.1-Python3-Portable.zip`](../../releases) (~12 MB)
2. **Extract**: Right-click → Extract All
3. **Run**: Double-click `PartitionFinder.exe`
4. **Enjoy**: Modern GUI with zero installation!

✅ No Python required  
✅ No libraries to install  
✅ Works on any Windows 10/11 PC  
✅ Fully portable (USB/network compatible)

📖 **[Complete Standalone Guide →](QUICK_START_INSTALLER.md)**

---

### Option 2: Python Installation

**For users with Python 3.8+ installed:**

```bash
# Clone repository
git clone https://github.com/yourusername/partitionfinder-python3.git
cd partitionfinder-python3

# Install dependencies
pip install -r requirements.txt

# Launch GUI
python gui_app.py
```

Or use quick launchers:
- **Windows**: `start_gui.bat`
- **Mac/Linux**: `python gui_app.py`

📖 **[GUI User Guide →](GUI_USER_GUIDE.md)** | **[Installation Guide →](HOW_TO_RUN.md)**

---

### Option 3: Command Line

```bash
# DNA analysis
python PartitionFinder.py examples/nucleotide

# Protein analysis  
python PartitionFinderProtein.py examples/aminoacid

# Morphology analysis
python PartitionFinderMorphology.py examples/morphology
```

📖 **[Command Line Documentation →](HOW_TO_RUN.md)**

---

## ✨ What's New

### 🎨 Modern GUI Interface
- **Professional dark theme** with intuitive controls
- **Large, user-friendly buttons** for easy navigation
- **Real-time colored logs** (🟢 SUCCESS | ⚠️ WARNING | ❌ ERROR)
- **Progress indicators** show analysis status
- **Auto-detection** of alignment files from config
- **Three analysis types**: DNA | Protein | Morphology

### 🔄 Enhanced Features
- **Automatic NEXUS→Phylip conversion** - No manual conversion needed!
- **Drag-and-drop file selection** for easy workflow
- **Built-in example datasets** for immediate testing
- **Standalone executable option** (Windows, ~12 MB download)
- **Portable** - Run from USB or network drives

### 🐍 Python 3 Compatibility
- ✅ **Python 3.8 - 3.12+** fully supported
- ✅ **Modern libraries**: NumPy 1.21+, Pandas 1.3+, SciPy 1.7+
- ✅ **30+ compatibility fixes** from Python 2.7
- ✅ **Cross-platform**: Windows, macOS, Linux

### 📊 Same Trusted Science
- ✅ All **algorithms unchanged** from original PartitionFinder 2
- ✅ Results **identical** to the original version
- ✅ **PhyML & RAxML** integration preserved
- ✅ All **analysis methods** supported (greedy, k-means, clustering)

---

## 📋 Requirements

### For Standalone Executable (Windows)
- **Nothing!** Just download and run.

### For Python Installation
- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**: Installed via `pip install -r requirements.txt`
  - numpy >= 1.21.0
  - pandas >= 1.3.0
  - scipy >= 1.7.0
  - scikit-learn >= 1.0.0
  - tables >= 3.7.0
  - pyparsing >= 3.0.0
  - psutil

### External Programs (Bundled)
- **PhyML** - For likelihood calculations
- **RAxML** - For phylogenetic inference

Both are included in the `programs/` folder.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[QUICK_START_INSTALLER.md](QUICK_START_INSTALLER.md)** | Guide for standalone executable users |
| **[GUI_USER_GUIDE.md](GUI_USER_GUIDE.md)** | Complete GUI documentation with screenshots |
| **[HOW_TO_RUN.md](HOW_TO_RUN.md)** | Python installation and command line usage |
| **[INSTALLER_BUILD_GUIDE.md](INSTALLER_BUILD_GUIDE.md)** | Build your own standalone executable |
| **[STANDALONE_VERIFICATION.md](STANDALONE_VERIFICATION.md)** | Technical verification of standalone build |

---

## 🎯 Features

- ✅ **Automatic model selection** from 56+ DNA models
- ✅ **Multiple search schemes**: Greedy, k-means clustering, hierarchical clustering
- ✅ **Supports multiple data types**: DNA, protein, morphology
- ✅ **AIC, AICc, and BIC** model selection criteria
- ✅ **Branch length optimization**
- ✅ **Multi-threading support** (RAxML-pthreads)
- ✅ **Comprehensive output** with detailed reports
- ✅ **Example datasets** included for testing

---

## 🖼️ Screenshots

### Modern GUI Interface
<img src="docs/gui-main.png" width="600" alt="Main GUI Interface">

### Real-Time Analysis Logs
<img src="docs/gui-logs.png" width="600" alt="Analysis Logs">

*(Screenshots to be added)*

---

## 📖 Usage Examples

### Example 1: DNA Analysis (GUI)
1. Launch `PartitionFinder.exe` or `python gui_app.py`
2. Select **"DNA"** analysis type
3. Browse to `examples/nucleotide/partition_finder.cfg`
4. Alignment auto-fills from config
5. Click **"START ANALYSIS"**
6. View real-time progress in log window
7. Results saved to `analysis/` folder

### Example 2: Protein Analysis (Command Line)
```bash
python PartitionFinderProtein.py examples/aminoacid
```

### Example 3: Using Your Own Data
Create a config file (`partition_finder.cfg`):
```ini
## ALIGNMENT FILE ##
alignment = your_alignment.nexus;

## BRANCHLENGTHS ##
branchlengths = linked;

## MODELS OF EVOLUTION ##
models = all;

## MODEL SELECTION ##
model_selection = aicc;

## SEARCH ##
search = greedy;

[data_blocks]
Gene1 = 1-500;
Gene2 = 501-1000;
Gene3 = 1001-1500;

[schemes]
search = all;
```

Then run:
```bash
python PartitionFinder.py /path/to/your/analysis/folder
```

---

## 🔧 Building Standalone Executable

### Windows
```bash
# Install PyInstaller
pip install pyinstaller

# Build portable package
build_portable.bat

# Output: PartitionFinder-2.1.1-Python3-Portable.zip
```

### Advanced Build Options
See **[INSTALLER_BUILD_GUIDE.md](INSTALLER_BUILD_GUIDE.md)** for:
- Custom builds
- Size optimization
- Windows installer creation (Inno Setup)
- Cross-platform builds

---

## 🧪 Testing

### Run Built-in Examples
```bash
# Test DNA analysis
python PartitionFinder.py examples/nucleotide

# Test Protein analysis
python PartitionFinderProtein.py examples/aminoacid

# Test Morphology analysis
python PartitionFinderMorphology.py examples/morphology
```

### Verify Installation
```bash
python -c "import numpy, pandas, scipy, sklearn, tables, pyparsing, psutil; print('All dependencies OK!')"
```

---

## 📊 What Gets Analyzed

PartitionFinder evaluates different ways to partition your alignment and selects the best partitioning scheme based on:

1. **Model Selection Criteria**: AIC, AICc, or BIC
2. **Search Algorithm**: Greedy, k-means, or hierarchical clustering
3. **Models Evaluated**: Up to 56 models for DNA, 18 for protein
4. **Branch Lengths**: Linked or unlinked across partitions

**Output includes:**
- Best partitioning scheme
- Best-fit models for each partition
- Model parameters
- Log-likelihood values
- Model selection statistics

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: GUI doesn't launch  
**Solution**: Install Python 3.8+ and dependencies: `pip install -r requirements.txt`

**Issue**: "PhyML not found"  
**Solution**: Check that `programs/phyml.exe` exists (Windows) or `programs/phyml` (Mac/Linux)

**Issue**: NEXUS file not recognized  
**Solution**: Ensure file has `#NEXUS` header and valid `MATRIX` block

**Issue**: "Windows protected your PC" (standalone exe)  
**Solution**: Click "More info" → "Run anyway" (this is normal for unsigned software)

**Issue**: Analysis hangs  
**Solution**: Check log window for errors. Verify input file formats.

For more help, see **[GUI_USER_GUIDE.md](GUI_USER_GUIDE.md)** or open an issue.

---

## 📜 License

This software is distributed under the **GNU General Public License v3.0**.

See [LICENSE](LICENSE) file for details.

**Includes:**
- PartitionFinder 2 - GPL v3
- PhyML - GPL v3
- RAxML - GPL v3
- Python libraries - Various open source licenses (BSD, MIT, PSF)

---

## 📝 Citation

If you use PartitionFinder in published work, please cite:

```
Lanfear, R., Frandsen, P. B., Wright, A. M., Senfeld, T., Calcott, B. (2016)
PartitionFinder 2: new methods for selecting partitioned models of evolution
for molecular and morphological phylogenetic analyses.
Molecular Biology and Evolution. DOI: 10.1093/molbev/msw260
```

**For this Python 3 port:**
```
PartitionFinder Python 3 Edition (2025)
Python 3 modernization with GUI
https://github.com/yourusername/partitionfinder-python3
```

---

## 👥 Credits

### Original PartitionFinder 2
- **Robert Lanfear** - Principal Developer
- **Brett Calcott** - Developer
- **Paul Frandsen** - Developer  
- **Ambuj Kumar** - Developer
- And many other contributors

**Original Project**: http://www.robertlanfear.com/partitionfinder/

### Python 3 Port & GUI
- Complete Python 3.8+ migration (30+ compatibility fixes)
- Modern GUI application with dark theme
- Automatic NEXUS conversion
- Standalone executable packaging
- Enhanced documentation

---

## 🤝 Contributing

Contributions are welcome! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/yourusername/partitionfinder-python3.git
cd partitionfinder-python3
pip install -r requirements.txt
python gui_app.py
```

---

## 🌟 Star This Repository

If you find this tool useful, please ⭐ star this repository to help others discover it!

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Original Project**: http://www.robertlanfear.com/partitionfinder/

---

## 📈 Version History

### Version 2.1.1 Python 3 (2025)
- ✅ Python 3.8 - 3.12+ support
- ✅ Modern GUI with dark theme
- ✅ Automatic NEXUS conversion
- ✅ Standalone Windows executable
- ✅ Updated dependencies
- ✅ Enhanced documentation

### Original Version 2.1.1 (2016)
- Python 2.7
- Command line only
- Original algorithms and features

---

## 🎉 Acknowledgments

Special thanks to:
- **Robert Lanfear** and the original PartitionFinder team
- **Python Software Foundation** for Python 3
- **NumPy, SciPy, Pandas** communities
- **PyInstaller** for standalone packaging
- All contributors to the phylogenetics community

---

<div align="center">

**[⬆ Back to Top](#partitionfinder-2---python-3-edition-)**

Made with ❤️ for the phylogenetics community

</div>
