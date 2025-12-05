# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all partfinder modules
partfinder_modules = collect_submodules('partfinder')

# Collect data files
datas = [
    ('partfinder', 'partfinder'),
    ('programs', 'programs'),
    ('examples', 'examples'),
    ('LICENSE', '.'),
    ('VERSION.txt', '.'),
    ('README.md', '.'),
    ('HOW_TO_RUN.md', '.'),
    ('GUI_USER_GUIDE.md', '.'),
    ('QUICK_START_INSTALLER.md', '.'),
]

# Hidden imports
hiddenimports = partfinder_modules + [
    'numpy',
    'pandas',
    'scipy',
    'scipy.special._cdflib',
    'sklearn',
    'sklearn.utils',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree',
    'sklearn.tree._utils',
    'tables',
    'pyparsing',
    'psutil',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
]

# Exclude unnecessary modules to reduce size
excludes = [
    'matplotlib',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'wheel',
    'pip',
    'pydoc',
    'doctest',
    'unittest',
    'test',
    'lib2to3',
    'distutils',
    'email',
    'http',
    'urllib3',
    'requests',
    'certifi',
    'sqlalchemy',
    'pydantic',
    'fastapi',
    'jinja2',
    'markupsafe',
    'pkg_resources',  # Causes AttributeError with PyInstaller
]

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    module_collection_mode={
        'pkg_resources': 'py',  # Avoid pkg_resources issues
    }
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PartitionFinder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PartitionFinder',
)
