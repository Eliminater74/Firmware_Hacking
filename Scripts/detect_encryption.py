import os
import subprocess
import struct

def detect_encryption(firmware_file):
    output_dir = "encryption_detection"
    os.makedirs(output_dir, exist_ok=True)

    with open(firmware_file, 'rb') as f:
        data = f.read()

    # Check for common encryption patterns
    encryption_patterns = {
        'AES': b'\x41\x45\x53',
        'RSA': b'\x52\x53\x41',
        'DES': b'\x44\x45\x53',
        'Blowfish': b'\x42\x6C\x6F\x77\x66\x69\x73\x68',
        'Twofish': b'\x54\x77\x6F\x66\x69\x73\x68',
        'Triple DES': b'\x54\x44\x45\x53'
    }

    detected_patterns = {}

    for name, pattern in encryption_patterns.items():
        if pattern in data:
            detected_patterns[name] = data.find(pattern)

    # Save results
    result_file = os.path.join(output_dir, "detection_results.txt")
    with open(result_file, 'w') as rf:
        for name, position in detected_patterns.items():
            rf.write(f"Detected {name} pattern at position {position}\n")

    if detected_patterns:
        print("Encryption patterns detected. See detection_results.txt for details.")
    else:
        print("No known encryption patterns detected.")

    return detected_patterns

if __name__ == "__main__":
    firmware_file = "be550v1-firmware.bin"  # Replace with your actual firmware file if needed
    detect_encryption(firmware_file)
