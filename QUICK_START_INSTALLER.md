# Quick Start - Standalone Installer

## For End Users (No Python Needed!)

### Windows Installation

1. **Download** `PartitionFinder-2.1.1-Python3-Portable.zip`
2. **Extract** the ZIP file to any folder
3. **Run** `PartitionFinder.exe` - that's it!

The application will open with a modern GUI. No Python installation required!

### Using the Application

1. **Select Analysis Type**: DNA, Protein, or Morphology
2. **Browse for Config File**: Click "📁 Browse" and select your `.cfg` file
3. **Browse for Alignment**: Select your `.nexus` or `.phy` file
4. **Optional**: Choose output directory
5. **Click** "▶ START ANALYSIS"
6. **Watch** real-time logs as analysis runs
7. **Done!** Results saved in `analysis` folder

### What's Included

✅ **Complete Python runtime** (~50 MB)
✅ **All scientific libraries** (numpy, pandas, scipy, etc.)
✅ **Analysis programs** (PhyML, RAxML)
✅ **Example datasets** (nucleotide, protein, morphology)
✅ **Full documentation**

### File Size

- **Portable ZIP**: ~150-200 MB (compressed)
- **Extracted folder**: ~300-400 MB
- **Why so large?** Includes Python interpreter + all scientific libraries

### System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk**: 500 MB free space
- **No Python installation needed!**

### Testing with Examples

Try the included examples:

1. Open PartitionFinder.exe
2. Select "DNA" analysis type
3. Browse to `examples/nucleotide/partition_finder.cfg`
4. The alignment file auto-fills
5. Click "START ANALYSIS"
6. Watch it work! (takes ~30 seconds)

### Troubleshooting

**"Windows protected your PC" message**
- This is normal for unsigned software
- Click "More info" → "Run anyway"
- Or: Extract to a trusted location first

**Antivirus warning**
- PyInstaller executables sometimes trigger false positives
- Add to antivirus exceptions
- The app is safe - all source code is included in the package

**Missing DLL errors**
- Install Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

**Slow startup**
- First launch may take 10-15 seconds (unpacking)
- Subsequent launches are faster

### File Structure

```
PartitionFinder/
├── PartitionFinder.exe       ← Run this!
├── programs/                  ← PhyML, RAxML
├── examples/                  ← Example data
│   ├── nucleotide/
│   ├── aminoacid/
│   └── morphology/
├── README.md
├── GUI_USER_GUIDE.md
└── [Python libraries bundled inside .exe]
```

### Running from Command Line

Advanced users can still use command line:

```cmd
cd PartitionFinder
PartitionFinder.exe examples\nucleotide
```

Or use the bundled scripts:
```cmd
python PartitionFinder.py examples\nucleotide
```

### Updating

To update:
1. Download new version
2. Extract to new folder
3. Copy your data files
4. Delete old version

### Network Installations

For lab/shared computers:
1. Extract to network drive (e.g., `\\server\apps\PartitionFinder\`)
2. Users run `\\server\apps\PartitionFinder\PartitionFinder.exe`
3. Each user gets own analysis folders

### Portable Use

The app is fully portable:
- ✅ Run from USB drive
- ✅ No registry changes
- ✅ No admin rights needed (after extraction)
- ✅ No installation traces

### Support

**Documentation:**
- `GUI_USER_GUIDE.md` - Complete GUI documentation
- `HOW_TO_RUN.md` - Command line usage
- `README.md` - General information

**Issues:**
1. Check log window for error details
2. Try example data to verify installation
3. Check file permissions
4. Verify input file formats

### Advanced: Building Your Own

Developers can build from source:

```powershell
# Clone or download source
git clone https://github.com/yourusername/partitionfinder-python3

# Install Python 3.12+
# Install dependencies
py -3.12 -m pip install -r requirements.txt

# Build portable package
build_portable.bat

# Creates: PartitionFinder-2.1.1-Python3-Portable.zip
```

See `INSTALLER_BUILD_GUIDE.md` for details.

### License

PartitionFinder is licensed under GPLv3. This includes:
- PartitionFinder code
- PhyML program
- RAxML program
- All bundled libraries

See `LICENSE` file for full terms.

### Citation

If you use this in published work, cite:

```
Lanfear, R., Frandsen, P. B., Wright, A. M., Senfeld, T., Calcott, B. (2016) 
PartitionFinder 2: new methods for selecting partitioned models of evolution 
for molecular and morphological phylogenetic analyses. 
Molecular biology and evolution. DOI: dx.doi.org/10.1093/molbev/msw260
```

### About This Port

This is an independent Python 3 modernization of PartitionFinder 2.
- **Original**: Python 2.7 (2016)
- **This version**: Python 3.8+ (2025)
- **Changes**: 30+ compatibility fixes, modern GUI added
- **Science**: Algorithms unchanged - results identical to original

---

**Questions?** See `GUI_USER_GUIDE.md` for complete documentation.

**Ready to analyze?** Just run `PartitionFinder.exe` and start!
