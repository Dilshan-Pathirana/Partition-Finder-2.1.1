"""
Convert NEXUS alignment files to PHYLIP format for PartitionFinder.
Usage: py -3.12 convert_nexus_to_phylip.py input.nexus output.phy
"""
import sys
import re

def parse_nexus(nexus_file):
    """Parse NEXUS file and extract sequences."""
    with open(nexus_file, 'r') as f:
        content = f.read()
    
    # Find the MATRIX block
    matrix_match = re.search(r'MATRIX\s+(.*?);', content, re.DOTALL | re.IGNORECASE)
    if not matrix_match:
        raise ValueError("No MATRIX block found in NEXUS file")
    
    matrix_text = matrix_match.group(1)
    
    sequences = {}
    for line in matrix_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Split on whitespace - first part is name, rest is sequence
        parts = line.split(None, 1)
        if len(parts) == 2:
            name, seq = parts
            seq = seq.replace(' ', '').replace('\t', '')  # Remove spaces
            
            if name in sequences:
                sequences[name] += seq  # Append for interleaved format
            else:
                sequences[name] = seq
    
    return sequences

def write_phylip(sequences, output_file):
    """Write sequences in PHYLIP format."""
    num_seqs = len(sequences)
    seq_length = len(next(iter(sequences.values())))
    
    # Verify all sequences have same length
    for name, seq in sequences.items():
        if len(seq) != seq_length:
            raise ValueError(f"Sequence {name} has different length: {len(seq)} vs {seq_length}")
    
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"{num_seqs} {seq_length}\n")
        
        # Write sequences
        for name, seq in sequences.items():
            # Pad name to 40 characters (phylip standard)
            padded_name = name[:40].ljust(40)
            f.write(f"{padded_name} {seq}\n")
    
    print(f"✓ Converted {num_seqs} sequences ({seq_length} bp) from NEXUS to PHYLIP")
    print(f"  Output: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py -3.12 convert_nexus_to_phylip.py input.nexus output.phy")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        sequences = parse_nexus(input_file)
        write_phylip(sequences, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
