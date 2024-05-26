import os
import binascii

# Define file paths
extracted_dir = "extracted_segments"
sections = ["AES_section.bin", "DES_section.bin", "RSA_section.bin"]

# Function to analyze a binary file
def analyze_section(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        hex_data = binascii.hexlify(data).decode('utf-8')
        print(f"Analysis of {file_path}:")
        print(f"Size: {len(data)} bytes")
        print(f"First 64 bytes (hex): {hex_data[:128]}")
        print("")

# Analyze each section
for section in sections:
    analyze_section(os.path.join(extracted_dir, section))
