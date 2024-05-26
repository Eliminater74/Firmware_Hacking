import os
import subprocess
import hashlib
from scipy.stats import entropy
import numpy as np
from binwalk import scan

def calculate_entropy(data):
    """Calculate the entropy of a given data block."""
    probabilities = np.bincount(np.frombuffer(data, dtype=np.uint8)) / len(data)
    return entropy(probabilities, base=2)

def run_binwalk(file_path):
    """Run binwalk on a file and return the result."""
    result = scan(file_path)
    return result

def extract_with_binwalk(file_path):
    """Run binwalk extraction on a file."""
    subprocess.run(['binwalk', '-e', file_path])

def run_foremost(file_path, output_dir):
    """Run foremost on a file."""
    subprocess.run(['foremost', '-i', file_path, '-o', output_dir])

def run_scalpel(file_path, output_dir):
    """Run scalpel on a file."""
    subprocess.run(['scalpel', file_path, '-o', output_dir])

def analyze_file(file_path):
    """Analyze a file using binwalk, foremost, and scalpel."""
    file_name = os.path.basename(file_path)
    output_dir_foremost = f"foremost_output_{file_name}"
    output_dir_scalpel = f"scalpel_output_{file_name}"

    print(f"Analyzing {file_path}...")

    # Run binwalk
    print("[+] Running binwalk...")
    binwalk_results = run_binwalk(file_path)
    extract_with_binwalk(file_path)

    # Run foremost
    print("[+] Running foremost...")
    run_foremost(file_path, output_dir_foremost)

    # Run scalpel
    print("[+] Running scalpel...")
    run_scalpel(file_path, output_dir_scalpel)

    # Calculate entropy
    print("[+] Calculating entropy...")
    with open(file_path, 'rb') as f:
        data = f.read()
        file_entropy = calculate_entropy(data)
        print(f"Entropy: {file_entropy:.4f}")

    # Display binwalk results
    for module in binwalk_results:
        for result in module.results:
            print(f"Offset: {result.offset}, Description: {result.description}")

    print("[+] Analysis complete.")

def main():
    firmware_file = 'firmware.bin'

    # Extract segments based on binwalk analysis
    segments = [
        (4928165, 11247057),
        (11247057, 23663218),
        (23663218, 23663218 + 1234567)  # Adjust this count as needed
    ]

    segment_files = []
    for i, (start, end) in enumerate(segments):
        segment_file = f'segment_{i+1}.bin'
        with open(firmware_file, 'rb') as f:
            f.seek(start)
            data = f.read(end - start)
            with open(segment_file, 'wb') as seg_f:
                seg_f.write(data)
        segment_files.append(segment_file)

    # Analyze each segment
    for segment_file in segment_files:
        analyze_file(segment_file)

if __name__ == "__main__":
    main()
