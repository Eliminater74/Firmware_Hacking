import os

# Define file paths
firmware_path = "be550v1-firmware.bin"
output_dir = "extracted_segments"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define the detected positions and patterns
detected_patterns = [
    {"name": "AES", "position": 41432945},
    {"name": "RSA", "position": 1994085},
    {"name": "DES", "position": 12938852}
]

# Function to extract section from firmware
def extract_section(firmware_path, output_path, start, length=4096):
    with open(firmware_path, "rb") as f:
        f.seek(start)
        data = f.read(length)
        with open(output_path, "wb") as out:
            out.write(data)

# Extract sections and save to output directory
for pattern in detected_patterns:
    output_path = os.path.join(output_dir, f"{pattern['name']}_section.bin")
    extract_section(firmware_path, output_path, pattern["position"])

print("Extraction completed. Check the extracted sections in the 'extracted_segments' directory.")
