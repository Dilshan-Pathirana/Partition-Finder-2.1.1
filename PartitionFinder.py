#!/usr/bin/env python3
# Copyright (C) 2012 Robert Lanfear and Brett Calcott
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# PartitionFinder also includes the PhyML program, the RAxML program, and the
# PyParsing library, all of which are protected by their own licenses and
# conditions, using PartitionFinder implies that you agree with those licences
# and conditions as well.

import sys
import os
import shutil

# Add the partfinder directory to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'partfinder'))

from partfinder import dependencies
from partfinder import main

if __name__ == "__main__":
    print("=" * 70)
    print("PartitionFinder - Interactive Mode")
    print("=" * 70)
    print()
    
    # Get NEXUS file path
    nexus_file = input("Enter the path to your NEXUS alignment file: ").strip().strip('"')
    if not os.path.exists(nexus_file):
        print(f"ERROR: File not found: {nexus_file}")
        sys.exit(1)
    
    # Get config file path
    cfg_file = input("Enter the path to your configuration file (.cfg): ").strip().strip('"')
    if not os.path.exists(cfg_file):
        print(f"ERROR: File not found: {cfg_file}")
        sys.exit(1)
    
    # Create output directory
    nexus_basename = os.path.splitext(os.path.basename(nexus_file))[0]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "examples", "results", f"{nexus_basename}_results")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy files to output directory
    nexus_dest = os.path.join(output_dir, os.path.basename(nexus_file))
    cfg_dest = os.path.join(output_dir, "partition_finder.cfg")
    
    shutil.copy2(nexus_file, nexus_dest)
    shutil.copy2(cfg_file, cfg_dest)
    
    # Update config file to point to the copied nexus file
    with open(cfg_dest, 'r') as f:
        cfg_content = f.read()
    
    # Replace alignment path in config
    import re
    cfg_content = re.sub(
        r'alignment\s*=\s*[^;]+;',
        f'alignment = {os.path.basename(nexus_file)};',
        cfg_content
    )
    
    with open(cfg_dest, 'w') as f:
        f.write(cfg_content)
    
    print()
    print(f"Analysis will be performed in: {output_dir}")
    print(f"Results will be saved in: {os.path.join(output_dir, 'analysis')}")
    print()
    print("Starting analysis...")
    print("=" * 70)
    print()
    
    # Set up sys.argv to pass the folder path to main
    sys.argv = ["PartitionFinder", output_dir, "--no-ml-tree"]
    
    try:
        sys.exit(main.main("PartitionFinder", "DNA"))
    except SystemExit as e:
        sys.exit(e.code if e.code is not None else 0)
