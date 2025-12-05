#!/usr/bin/env python3
"""
NEXUS File Diagnostic Tool
Inspects NEXUS files to understand their structure
"""
import sys
import re

def diagnose_nexus(filepath):
    """Diagnose NEXUS file structure"""
    print(f"=" * 70)
    print(f"NEXUS File Diagnostic: {filepath}")
    print(f"=" * 70)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        print(f"\n✓ File size: {len(content)} bytes")
        print(f"✓ Number of lines: {len(content.splitlines())}")
        
        # Check for NEXUS header
        if content.upper().startswith('#NEXUS'):
            print(f"✓ Valid NEXUS header found")
        else:
            print(f"⚠ Warning: No #NEXUS header found")
        
        # Find all BEGIN blocks
        print(f"\n📦 BEGIN Blocks Found:")
        begin_blocks = re.findall(r'BEGIN\s+(\w+)\s*;', content, re.IGNORECASE)
        for block in begin_blocks:
            print(f"  • {block.upper()}")
        
        # Check for MATRIX keyword
        matrix_matches = list(re.finditer(r'MATRIX', content, re.IGNORECASE))
        print(f"\n🔍 MATRIX keyword found: {len(matrix_matches)} time(s)")
        
        if matrix_matches:
            for i, match in enumerate(matrix_matches, 1):
                start = match.start()
                end = min(start + 500, len(content))
                preview = content[start:end]
                print(f"\n  MATRIX occurrence {i} at position {start}:")
                print(f"  Preview (first 500 chars):")
                print(f"  {'-' * 60}")
                for line_num, line in enumerate(preview.split('\n')[:10], 1):
                    print(f"  {line_num:3}: {line}")
                print(f"  {'-' * 60}")
        
        # Check for NTAX and NCHAR
        ntax_match = re.search(r'NTAX\s*=\s*(\d+)', content, re.IGNORECASE)
        nchar_match = re.search(r'NCHAR\s*=\s*(\d+)', content, re.IGNORECASE)
        
        if ntax_match:
            print(f"\n📊 NTAX (number of taxa): {ntax_match.group(1)}")
        if nchar_match:
            print(f"📊 NCHAR (number of characters): {nchar_match.group(1)}")
        
        # Look for what looks like sequence data
        print(f"\n🧬 Looking for sequence-like data...")
        lines_with_sequences = []
        for i, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('['):
                continue
            # Look for lines that might be sequences
            if re.search(r'^[A-Za-z_][A-Za-z0-9_-]*\s+[ACGTNacgtn\-\?]+', line):
                lines_with_sequences.append((i, line[:80]))
        
        if lines_with_sequences:
            print(f"✓ Found {len(lines_with_sequences)} lines that look like sequences")
            print(f"  First few examples:")
            for line_num, line in lines_with_sequences[:5]:
                print(f"  Line {line_num}: {line}")
        else:
            print(f"⚠ No lines that look like sequences found!")
        
        # Check file format
        print(f"\n📋 Format Assessment:")
        if 'INTERLEAVE' in content.upper():
            print(f"  • Interleaved format detected")
        else:
            print(f"  • Sequential format (or not specified)")
        
        if 'DATATYPE' in content.upper():
            datatype_match = re.search(r'DATATYPE\s*=\s*(\w+)', content, re.IGNORECASE)
            if datatype_match:
                print(f"  • DATATYPE: {datatype_match.group(1)}")
        
        print(f"\n" + "=" * 70)
        print(f"Diagnosis complete!")
        print(f"=" * 70)
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python diagnose_nexus.py <nexus_file>")
        sys.exit(1)
    
    sys.exit(diagnose_nexus(sys.argv[1]))
