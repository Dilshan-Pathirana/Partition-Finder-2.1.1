# Building a Standalone Installer for PartitionFinder

This guide explains how to create a single executable installer that bundles Python and all dependencies.

## Prerequisites

1. **Python 3.8+** installed
2. **All dependencies** installed (`pip install -r requirements.txt`)

## Quick Build (Portable Package)

### Windows:

```powershell
# Install PyInstaller and build
py -3.12 build_installer.py
```

This creates:
- `dist/PartitionFinder/` - Folder with executable
- `PartitionFinder-2.1.1-Python3-Portable.zip` - Portable package

**Distribution**: Share the .zip file. Users extract and run `PartitionFinder.exe` - no Python needed!

## Advanced: Windows Installer (.exe)

For a professional installer with Start Menu shortcuts:

### 1. Install Inno Setup

Download from: https://jrsoftware.org/isdl.php

### 2. Build Executable First

```powershell
py -3.12 build_installer.py
```

### 3. Create Installer

Open Inno Setup Compiler:
1. File → Open → `installer_setup.iss`
2. Build → Compile
3. Find installer in `installer_output/`

Result: `PartitionFinder-2.1.1-Python3-Setup.exe`

## What Gets Bundled

✅ **Python runtime** (no Python installation needed)
✅ **All dependencies** (numpy, pandas, scipy, etc.)
✅ **Analysis programs** (PhyML, RAxML executables)
✅ **Example data** (nucleotide, protein, morphology)
✅ **Documentation** (HOW_TO_RUN.md, GUI_USER_GUIDE.md)

## Distribution Options

### Option 1: Portable ZIP (Recommended)
- **Size**: ~150-200 MB
- **Pros**: No installation, works from USB drive
- **Cons**: Larger file size
- **Best for**: Quick sharing, temporary use

### Option 2: Windows Installer
- **Size**: ~150-200 MB (compressed)
- **Pros**: Professional, Start Menu integration, uninstaller
- **Cons**: Requires admin rights to install
- **Best for**: Lab computers, permanent installations

### Option 3: Folder Distribution
- Just share `dist/PartitionFinder/` folder
- Users run `PartitionFinder.exe` directly
- **Best for**: Network drives, shared folders

## File Size Optimization

To reduce size, edit `partfinder_gui.spec`:

```python
excludes=[
    'matplotlib',      # Not used
    'IPython',         # Not used
    'jupyter',         # Not used
    'test',            # Test modules
    'unittest',        # Test modules
]
```

Then rebuild:
```powershell
py -3.12 -m PyInstaller partfinder_gui.spec --clean
```

## Testing the Installer

### Test Portable Package:
1. Extract `PartitionFinder-2.1.1-Python3-Portable.zip`
2. Run `PartitionFinder.exe`
3. Try example analysis: `examples/nucleotide`

### Test Windows Installer:
1. Run `PartitionFinder-2.1.1-Python3-Setup.exe`
2. Follow installation wizard
3. Launch from Start Menu
4. Test with example data

## Troubleshooting

### "Missing module" error
Add to `hiddenimports` in `partfinder_gui.spec`:
```python
hiddenimports=[
    'missing_module_name',
]
```

### Large file size
- Remove unused examples from `datas` section
- Add more modules to `excludes`
- Use UPX compression (already enabled)

### Antivirus false positive
- Sign the executable (requires code signing certificate)
- Submit to antivirus vendors as false positive
- Use Inno Setup installer (more trusted)

## Build on Other Platforms

### macOS:
```bash
python3 build_installer.py
```
Creates `.app` bundle in `dist/`

### Linux:
```bash
python3 build_installer.py
```
Creates executable in `dist/PartitionFinder/`

## Continuous Integration

For automated builds, use GitHub Actions:

```yaml
- name: Build Installer
  run: python build_installer.py
  
- name: Upload Artifact
  uses: actions/upload-artifact@v3
  with:
    name: PartitionFinder-Portable
    path: PartitionFinder-*.zip
```

## Distribution Checklist

Before distributing:
- ✅ Test on clean Windows machine (no Python)
- ✅ Test all three analysis types (DNA, Protein, Morphology)
- ✅ Test with user's own data files
- ✅ Verify example data works
- ✅ Check file size is reasonable (<250 MB)
- ✅ Include README in package
- ✅ Test uninstaller (if using Inno Setup)

## Support

Users report issues:
1. Check log files in analysis folder
2. Run from command line to see errors:
   ```
   PartitionFinder.exe --debug
   ```
3. Check antivirus isn't blocking

## Version Updates

To update version:
1. Edit version in `build_installer.py`
2. Edit version in `installer_setup.iss`
3. Edit version in `gui_app.py` title
4. Rebuild all packages

## File Structure in Package

```
PartitionFinder/
├── PartitionFinder.exe       # Main executable
├── programs/                  # Analysis tools
│   ├── phyml.exe
│   └── raxml.exe
├── partfinder/               # Python modules (bundled)
├── examples/                 # Example data
│   ├── nucleotide/
│   ├── aminoacid/
│   └── morphology/
├── LICENSE
├── README.md
├── HOW_TO_RUN.md
└── GUI_USER_GUIDE.md
```

All Python dependencies are bundled inside the executable - users never see them!
