import os

# Define file paths
firmware_path = "be550v1-firmware.bin"
output_dir = "high_entropy_sections"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List of high entropy positions (manually chosen based on your analysis)
high_entropy_positions = [
    0, 4096, 8192, 12288, 16384, 20480, 24576, 28672, 32768, 36864,
    40960, 45056, 49152, 53248, 57344, 61440, 65536, 69632, 73728,
    77824, 81920, 86016, 90112, 94208, 98304, 102400, 106496, 110592,
    114688, 118784, 122880, 126976, 131072
]

# Function to extract section from firmware
def extract_section(firmware_path, output_path, start, length=4096):
    with open(firmware_path, "rb") as f:
        f.seek(start)
        data = f.read(length)
        with open(output_path, "wb") as out:
            out.write(data)

# Extract high entropy sections and save to output directory
for position in high_entropy_positions:
    output_path = os.path.join(output_dir, f"section_{position}.bin")
    extract_section(firmware_path, output_path, position)

print("Extraction of high entropy sections completed.")
