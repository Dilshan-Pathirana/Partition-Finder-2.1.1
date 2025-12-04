# How to Run PartitionFinder 2 - Python 3 Edition

A simple guide to install Python, set up PartitionFinder, and analyze your DNA/protein data.

---

## About This Version

This is a **completely modernized version** of PartitionFinder 2, rebuilt from the original Python 2.7 codebase to work with **Python 3.8+** (tested on Python 3.12).

**What's Changed:**
- ✅ Full Python 3.8+ compatibility (30+ code fixes)
- ✅ Updated dependencies (numpy, pandas, scipy, scikit-learn latest versions)
- ✅ Fixed deprecated functions (time.clock, imp module, etc.)
- ✅ Resolved all bytes/string encoding issues
- ✅ Modern package management with pip
- ✅ Cross-platform support (Windows, Mac, Linux)

**Original Project:** PartitionFinder 2 by Lanfear et al. (2016)  
**This Modernization:** Python 3 migration and compatibility fixes (December 2025)

> **Note:** This is a separate, updated version and is NOT affiliated with or endorsed by the original PartitionFinder team. All scientific algorithms remain unchanged from the original.

---

## Step 1: Install Python

### Windows:
1. Go to https://www.python.org/downloads/
2. Download **Python 3.12** or newer (click the big yellow button)
3. Run the installer
4. ⚠️ **IMPORTANT**: Check the box "Add Python to PATH" at the bottom
5. Click "Install Now"
6. After installation, open Command Prompt and type: `python --version`
7. You should see something like "Python 3.12.x"

### Mac:
1. Go to https://www.python.org/downloads/
2. Download **Python 3.12** or newer
3. Run the installer and follow the instructions
4. Open Terminal and type: `python3 --version`

### Linux:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## Step 2: Open Project in VS Code

1. **Install VS Code** if you don't have it: https://code.visualstudio.com/
2. Open VS Code
3. Go to **File → Open Folder**
4. Select the `test-demonstrations` folder
5. VS Code will open the project

## Step 3: Install PartitionFinder Dependencies

In VS Code:
1. Press **Ctrl + `** (backtick) to open the integrated terminal
2. The terminal opens at the project folder automatically
3. Install all required packages:

**Windows:**
```bash
py -3.12 -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip install -r requirements.txt
```

This installs:
- numpy (for calculations)
- pandas (for data handling)
- pytables (for file storage)
- pyparsing (for reading configuration)
- scipy (for statistics)
- scikit-learn (for clustering algorithms)

**Wait until you see "Successfully installed..."** - this may take a few minutes.

---

## Step 4: Prepare Your Data

### What you need:
1. **An alignment file** (`.phy` format) - your DNA/protein sequences
2. **A configuration file** (`partition_finder.cfg`) - tells the program what to do

### Where to put your files:

Create a folder for your analysis, for example:
```
my_analysis/
  ├── my_sequences.phy
  └── partition_finder.cfg
```

### Example configuration file:

Create a file called `partition_finder.cfg` with this content:

```
## ALIGNMENT FILE ##
alignment = my_sequences.phy;

## BRANCHLENGTHS: linked | unlinked ##
branchlengths = linked;

## MODELS OF EVOLUTION: all | mrbayes | beast | gamma | gammaI | <list> ##
models = GTR, GTR+G, GTR+I+G;

## MODEL SELECTION: AIC | AICc | BIC ##
model_selection = aicc;

## SEARCH: all | user | greedy | rcluster | rclusterf | kmeans ##
search = greedy;

[data_blocks]
Gene1_pos1 = 1-789\3;
Gene1_pos2 = 2-789\3;
Gene1_pos3 = 3-789\3;

[schemes]
search = all;
```

**Need help with configuration?** Look at the examples in the `examples/` folder:
- `examples/nucleotide/` - for DNA data
- `examples/aminoacid/` - for protein data
- `examples/morphology/` - for morphological data

---

## Step 5: Run PartitionFinder

In VS Code, make sure the integrated terminal is open (**Ctrl + `**).

### For DNA/Nucleotide data:

Type this in the terminal:

**Windows:**
```bash
p
```

**Mac/Linux:**
```bash
python3 PartitionFinder.py path/to/your/my_analysis
```

### For Protein/Amino acid data:

Type this in the terminal:

**Windows:**
```bash
py -3.12 PartitionFinderProtein.py examples/aminoacid
```

**Mac/Linux:**
```bash
python3 PartitionFinderProtein.py path/to/your/my_analysis
```

### For Morphological data:

Type this in the terminal:

**Windows:**
```bash
py -3.12 PartitionFinderMorphology.py examples/morphology --raxml
```

**Mac/Linux:**
```bash
python3 PartitionFinderMorphology.py path/to/your/my_analysis --raxml
```

### Quick Test Example:

Run this to test with example data:

**Windows:**
```bash
py -3.12 PartitionFinder.py examples/nucleotide
```

**Mac/Linux:**
```bash
python3 PartitionFinder.py examples/nucleotide
```

**Watch the terminal** - you'll see progress messages as it runs (takes about 10-20 seconds).

---

## Step 6: Find Your Results

After the program finishes, look in VS Code's Explorer panel (left side) in your analysis folder:

```
my_analysis/
  └── analysis/
      ├── best_scheme.txt  ← **YOUR MAIN RESULTS**
      ├── schemes/         (detailed results for each tested scheme)
      ├── subsets/         (individual model results)
      └── start_tree/      (phylogenetic tree files)
```

### What's in `best_scheme.txt`:
- **Best partitioning scheme** - how to divide your data
- **Model for each partition** - which evolutionary model fits best
- **Statistics** (AICc scores, log-likelihood)
- **Ready-to-use formats** for:
  - RAxML (phylogenetic analysis)
  - MrBayes (Bayesian analysis)
  - IQTree (fast likelihood analysis)
  - NEXUS format

**To view results:** Click on `best_scheme.txt` in VS Code's Explorer to open and read it.

---

## Common Problems

### "python is not recognized" or "py is not recognized"
- You didn't check "Add Python to PATH" during installation
- **Fix**: Reinstall Python 3.12 and check that box
- **Windows**: Use `py -3.12` command to run with Python 3.12
- **Mac/Linux**: Use `python3` command instead of `python`
- **VS Code tip**: You can also select the Python interpreter by pressing **Ctrl+Shift+P** and typing "Python: Select Interpreter"

### "No module named 'numpy'" (or other package)
- Dependencies not installed
- **Fix Windows**: In VS Code terminal, run `py -3.12 -m pip install -r requirements.txt`
- **Fix Mac/Linux**: In VS Code terminal, run `pip install -r requirements.txt` or `pip3 install -r requirements.txt`

### "Could not find alignment file"
- Wrong path to your analysis folder
- **Fix**: In VS Code, you can right-click a folder in the Explorer and "Copy Path", then paste it in the command
- Example: `python PartitionFinder.py "C:\Users\YourName\my_analysis"`

### Program runs but produces errors
- Check your `.phy` file is valid (proper PHYLIP format)
- Check your `partition_finder.cfg` file has correct syntax
- Look at the examples in `examples/` folder for reference

### Terminal not showing in VS Code
- Press **Ctrl + `** (backtick key, usually above Tab)
- Or go to **View → Terminal** in the menu

---

## What This Program Does

PartitionFinder helps you:
1. **Find the best way to partition your genetic data** (which genes/sites should be analyzed together)
2. **Select the best evolutionary models** for each partition
3. **Prepare files** for popular phylogenetic programs (RAxML, MrBayes, IQTree)

This is essential before running phylogenetic analyses to get accurate evolutionary trees.

---

## Need More Help?

- Read `README.md` for detailed documentation
- Check example files in `examples/` folder
- Original paper: Lanfear et al. (2016) Molecular Biology and Evolution

---

## Citation

If you use PartitionFinder in your research, please cite:

> Lanfear, R., Frandsen, P. B., Wright, A. M., Senfeld, T., Calcott, B. (2016)  
> PartitionFinder 2: new methods for selecting partitioned models of evolution for molecular and morphological phylogenetic analyses.  
> Molecular Biology and Evolution. DOI: dx.doi.org/10.1093/molbev/msw260

---

---

## Distribution Information

**Version:** PartitionFinder 2 - Python 3 Edition (v2.1.1-py3)  
**Release Date:** December 2025  
**Python Requirements:** Python 3.8+ (Tested on 3.12)  
**Platform Support:** Windows, macOS, Linux

### Package Contents

```
PartitionFinder2-Python3/
├── HOW_TO_RUN.md              (This file - complete user guide)
├── LICENSE                     (GPL v3 License)
├── requirements.txt            (Python dependencies)
├── PartitionFinder.py          (Main program - DNA/nucleotide data)
├── PartitionFinderProtein.py   (For protein/amino acid data)
├── PartitionFinderMorphology.py (For morphological data)
├── partfinder/                 (Core Python modules)
├── programs/                   (PhyML and RAxML binaries)
└── examples/                   (Example datasets for testing)
    ├── nucleotide/            (DNA example)
    ├── aminoacid/             (Protein example)
    └── morphology/            (Morphology example)
```

### Known Limitations

- K-means clustering algorithm may be slow for large datasets
- Morphological data requires `--raxml` flag
- Windows users must use `py -3.12` command (not `python`)

### Support & Issues

This is an unofficial Python 3 port. For issues with:
- **This Python 3 version:** Check your Python/dependency installation first
- **Scientific algorithms:** Refer to original PartitionFinder 2 documentation and papers

### Credits

**Original Software:**
- Robert Lanfear, Paul B. Frandsen, Alyssa M. Wright, Tara Senfeld, Brett Calcott
- PartitionFinder 2: Molecular Biology and Evolution (2016)
- DOI: 10.1093/molbev/msw260

**Python 3 Modernization:**
- Migration from Python 2.7 to Python 3.8+
- Bug fixes and compatibility updates
- December 2025

---

**Ready to use! See Step 1 above to get started.**
