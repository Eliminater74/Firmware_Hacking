import os
import subprocess
from scipy.stats import entropy
import numpy as np

def calculate_entropy(data):
    prob = np.bincount(data) / len(data)
    return entropy(prob, base=2)

def analyze_file(file_path):
    print(f"File analysis for {file_path}:")
    result = subprocess.run(['file', file_path], stdout=subprocess.PIPE)
    print(result.stdout.decode())

    print("\nStrings output:")
    result = subprocess.run(['strings', file_path], stdout=subprocess.PIPE)
    print(result.stdout.decode())

    print("\nHexdump output:")
    result = subprocess.run(['hexdump', '-C', file_path], stdout=subprocess.PIPE)
    print(result.stdout.decode())

    with open(file_path, 'rb') as f:
        data = f.read()
        ent = calculate_entropy(np.frombuffer(data, dtype=np.uint8))
        print("\nEntropy analysis:")
        print(f"Entropy: {ent:.4f}")

def recursive_analysis(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            analyze_file(file_path)
            extract_with_foremost(file_path)

def extract_with_foremost(file_path):
    output_dir = f"{file_path}_foremost"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nRunning foremost on {file_path}...")
    result = subprocess.run(['foremost', '-i', file_path, '-o', output_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode())
    print(result.stderr.decode())

def main():
    firmware_path = "firmware.bin"
    output_dir = "enhanced_extracted"

    # Run binwalk with extraction
    subprocess.run(['binwalk', '--extract', firmware_path, '-C', output_dir])

    # Perform recursive analysis on extracted files
    recursive_analysis(output_dir)

if __name__ == "__main__":
    main()
