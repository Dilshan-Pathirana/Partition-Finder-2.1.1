# Changelog

All notable changes to PartitionFinder Python 3 Edition will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.1-py3] - 2024-12-18

### 🎉 Initial Python 3 Release

This is the first Python 3 compatible release of PartitionFinder 2, with major modernization updates.

### ✨ Added

#### GUI Application
- **Brand new GUI** with modern dark theme (#1E1E1E)
- **Large, user-friendly buttons** for easy navigation
- **Real-time colored logs** (🟢 SUCCESS | ⚠️ WARNING | ❌ ERROR | ℹ️ INFO)
- **Progress indicators** showing analysis status
- **Drag-and-drop file selection** workflow
- **Three analysis types**: DNA, Protein, Morphology
- **Auto-detection** of alignment files from configuration
- **Built-in example selection** for quick testing

#### Standalone Distribution
- **Windows standalone executable** (~12 MB)
- **Zero-installation** - works without Python
- **Fully portable** - runs from USB or network drives
- **Bundled dependencies** - Python 3.12 + all libraries
- **Included programs** - PhyML, RAxML, RAxML-pthreads
- **Complete examples** - nucleotide, aminoacid, morphology datasets

#### File Format Support
- **Automatic NEXUS→Phylip conversion** built into alignment loader
- **Detects file format** automatically (.nexus, .nex, .phy)
- **Handles interleaved NEXUS** files
- **Preserves original files** - creates temporary phylip for analysis
- **No manual conversion needed** - seamless workflow

#### Documentation
- `README.md` - Comprehensive GitHub landing page
- `QUICK_START_INSTALLER.md` - Standalone executable guide
- `GUI_USER_GUIDE.md` - Complete GUI documentation
- `HOW_TO_RUN.md` - Python installation and CLI usage
- `INSTALLER_BUILD_GUIDE.md` - Build instructions for developers
- `STANDALONE_VERIFICATION.md` - Technical verification report
- `DISTRIBUTION_READY.md` - Release checklist
- `CONTRIBUTING.md` - Contribution guidelines
- `VERSION.txt` - Version tracking

#### Build Infrastructure
- `build_portable.bat` - Windows batch script for building
- `partfinder_gui.spec` - PyInstaller configuration
- `requirements.txt` - Updated dependencies for Python 3

### 🔄 Changed

#### Python 3 Migration (30+ fixes)
- **Migrated to Python 3.8+** from Python 2.7
- **Updated print statements** - `print(x)` instead of `print x`
- **Fixed integer division** - Explicit `//` for floor division
- **Dictionary methods** - `.keys()`, `.values()`, `.items()` return views
- **String/bytes handling** - Proper encoding/decoding
- **Iterator updates** - `map()`, `filter()` return iterators
- **Exception syntax** - Modern `except Exception as e:`
- **Relative imports** - PEP 8 compliant import structure
- **Unicode handling** - Native string support
- **Range/xrange** - Using `range()` everywhere

#### Dependencies Updated
- **numpy** 1.5.1 → 1.21.0+ (Python 3 compatible)
- **pandas** 0.9.0 → 1.3.0+ (with modern API)
- **scipy** 0.9.0 → 1.7.0+ (optimized algorithms)
- **scikit-learn** 0.11 → 1.0.0+ (new estimator API)
- **tables (PyTables)** 2.x → 3.7.0+ (HDF5 compatibility)
- **pyparsing** 1.x → 3.0.0+ (updated parser)
- **Added psutil** - for system resource monitoring

#### Code Improvements
- **Type annotations** where appropriate
- **Better error handling** with descriptive messages
- **Logging improvements** with colors and emojis
- **Path handling** using `pathlib` where beneficial
- **Configuration parsing** more robust
- **File I/O** with context managers (`with` statements)

### 🐛 Fixed

- **Partition definition handling** - Fixed range mismatches in test data
- **NEXUS parser** - Handles various NEXUS formats correctly
- **Character set parsing** - Proper handling of codon positions
- **File path handling** - Cross-platform compatibility
- **Memory management** - Better cleanup of temporary files
- **Threading issues** - Improved multi-core support
- **GUI freezing** - Analysis runs in separate thread
- **Log output** - Proper Unicode handling in logs

### 🔧 Maintained

#### Core Algorithms (Unchanged)
- ✅ All partitioning algorithms identical to original
- ✅ Model selection criteria (AIC, AICc, BIC) unchanged
- ✅ PhyML integration preserved
- ✅ RAxML integration preserved
- ✅ Greedy search algorithm identical
- ✅ K-means clustering identical
- ✅ Hierarchical clustering identical
- ✅ All 56+ DNA models supported
- ✅ Protein model support unchanged
- ✅ Morphology analysis unchanged

**Results are scientifically identical** to the original PartitionFinder 2.

### 📊 Technical Details

- **Python Runtime**: 3.8 - 3.12+ supported
- **Package Size**: 11.99 MB (compressed ZIP)
- **Extracted Size**: 29.15 MB (with all libraries)
- **Bundled Python**: 3.12.7 (in standalone executable)
- **Build Tool**: PyInstaller 6.17.0
- **License**: GNU GPL v3 (unchanged)

### 🙏 Credits

- **Original PartitionFinder 2**: [Robert Lanfear et al.](http://www.robertlanfear.com/partitionfinder/)
- **Python 3 Migration**: Updated for modern Python ecosystem
- **GUI Development**: New tkinter-based interface
- **Community**: All testers and contributors

---

## [2.1.0] - 2014-08-15

### Original PartitionFinder 2 Release

See original repository for pre-Python 3 history:
- [PartitionFinder 2 Original](http://www.robertlanfear.com/partitionfinder/)

---

## Future Releases

### Planned Features
- macOS standalone application (.app bundle)
- Linux AppImage distribution
- Automated testing (CI/CD)
- Results visualization in GUI
- More analysis presets
- Configuration templates
- Batch processing support

---

**Format**: `[Version] - YYYY-MM-DD`

**Types of Changes**:
- `Added` - New features
- `Changed` - Changes to existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes
