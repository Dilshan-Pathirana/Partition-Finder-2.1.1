# PartitionFinder GUI User Guide

## Getting Started

### Launching the Application

**Windows:**
1. Navigate to the PartitionFinder folder
2. Double-click `start_gui.bat`
3. The GUI window will open

**Mac/Linux:**
```bash
python3 gui_app.py
```

## Using the GUI

### Step 1: Select Analysis Type

At the top of the window, choose your data type:
- **DNA** - For nucleotide sequences
- **Protein** - For amino acid sequences  
- **Morphology** - For morphological data

### Step 2: Select Input Files

#### Config File (.cfg)
1. Click **Browse** next to "Config File"
2. Navigate to your `.cfg` configuration file
3. Select and open it
4. The app will try to auto-detect your alignment file

#### Alignment File
1. Click **Browse** next to "Alignment File"
2. Choose your alignment file:
   - NEXUS format: `.nexus`, `.nex` (recommended)
   - Phylip format: `.phy`
3. The app automatically converts NEXUS to phylip if needed

#### Output Directory (Optional)
1. Click **Browse** next to "Output Directory"
2. Choose where to save results
3. If not specified, results save to the config file's folder

### Step 3: Run Analysis

1. Click **▶ Start Analysis** button
2. Watch real-time progress in the log window:
   - **Black text** = Info messages
   - **Orange text** = Warnings
   - **Red text** = Errors
   - **Green text** = Success messages
3. Progress bar shows activity
4. Status bar at bottom shows current state

### Step 4: View Results

When complete:
- A success message appears
- Results are in the `analysis` folder
- Key files:
  - `best_scheme.txt` - Best partitioning scheme
  - `analysis.log` - Full analysis log
  - Various `.csv` files with detailed results

## Features

### Real-Time Logging
- See every step as it happens
- Color-coded messages for easy reading
- Timestamps on all messages
- Scroll through history

### Error Handling
- Clear error messages
- Debugging information in logs
- Validation before running
- Safe stop button if needed

### File Format Support
- **NEXUS** (.nexus, .nex) - Automatically converted
- **Phylip** (.phy) - Used directly
- No manual conversion needed!

### Controls

**Start Analysis** - Begin the partition analysis

**Stop** - Halt a running analysis (enabled during run)

**Clear Logs** - Empty the log window

## Troubleshooting

### "Please select a configuration file"
- You must choose a `.cfg` file first
- Use the Browse button next to "Config File"

### "Configuration file does not exist"
- The file path is invalid
- Browse again and select a valid file

### "Please select an alignment file"
- You must choose an alignment file
- Supported: `.nexus`, `.nex`, `.phy`

### "Alignment file does not exist"
- The file path is invalid
- Browse again and select a valid file

### Analysis Fails
1. Check the log window for error messages
2. Red text shows specific errors
3. Common issues:
   - Missing sites in data blocks
   - Mismatched file formats
   - Invalid config settings

### Python Not Found
- Install Python 3.8 or higher
- Windows: Use the py launcher (`py -3.12`)
- Make sure Python is in your PATH

## Example Workflow

1. **Open GUI**
   - Windows: Double-click `start_gui.bat`
   - Mac/Linux: Run `python3 gui_app.py`

2. **Select Analysis Type**
   - Choose "DNA" (most common)

3. **Browse for Config**
   - Navigate to `examples/nucleotide/partition_finder.cfg`
   - The alignment file auto-fills

4. **Start Analysis**
   - Click "▶ Start Analysis"
   - Watch the log for progress

5. **Review Results**
   - Check `examples/nucleotide/analysis/best_scheme.txt`

## Tips

✅ **Auto-detection** - The app reads your config file and finds the alignment automatically

✅ **NEXUS support** - Use NEXUS files directly; conversion happens automatically

✅ **Watch logs** - The log window shows exactly what's happening

✅ **Save logs** - Copy/paste from log window for debugging

✅ **Multiple runs** - Close and reopen to run different analyses

✅ **No terminal needed** - Everything works in the GUI

## Technical Details

**Supported Formats:**
- Config: `.cfg` (PartitionFinder format)
- Alignment: `.nexus`, `.nex`, `.phy`

**Output Files:**
- `analysis/` folder in same directory as config
- Or in your chosen output directory
- Timestamped folders if running multiple times

**Requirements:**
- Python 3.8+
- Dependencies from `requirements.txt`
- See HOW_TO_RUN.md for installation

## Need Command Line?

Advanced users can still use the command line:

**DNA:**
```bash
py -3.12 PartitionFinder.py examples/nucleotide
```

**Protein:**
```bash
py -3.12 PartitionFinderProtein.py examples/aminoacid
```

**Morphology:**
```bash
py -3.12 PartitionFinderMorphology.py examples/morphology --raxml
```

See `HOW_TO_RUN.md` for full command line documentation.

## Support

For issues:
1. Check the log window for error details
2. Review HOW_TO_RUN.md for setup
3. Verify your config file format
4. Test with example data first

## Updates

This GUI is part of PartitionFinder 2.1.1 Python 3 Edition.
- Modern Python 3.8+ codebase
- Automatic NEXUS conversion built-in
- Real-time logging and debugging
- No coding experience required!
