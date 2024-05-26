#!/usr/bin/env python3

import os
import subprocess

def analyze_firmware(firmware_file):
    output_dir = "analyzed"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Run binwalk with -A to identify instructions
        binwalk_output = subprocess.check_output(['binwalk', '-A', firmware_file], stderr=subprocess.STDOUT, timeout=60).decode('utf-8')
        with open(os.path.join(output_dir, 'binwalk_analysis.txt'), 'w') as f:
            f.write(binwalk_output)
        print("Binwalk analysis saved to binwalk_analysis.txt")

        # Create a hexdump of the firmware
        hexdump_file = os.path.join(output_dir, 'firmware.hexdump')
        with open(hexdump_file, 'wb') as hd:
            hexdump = subprocess.check_output(['xxd', firmware_file])
            hd.write(hexdump)
        print(f"Hexdump saved to {hexdump_file}")

        # Additional entropy analysis for detecting encrypted data
        entropy_output = subprocess.check_output(['ent', firmware_file]).decode('utf-8')
        with open(os.path.join(output_dir, 'entropy_analysis.txt'), 'w') as f:
            f.write(entropy_output)
        print("Entropy analysis saved to entropy_analysis.txt")

    except subprocess.TimeoutExpired:
        print("Operation timed out.")
        return
    except subprocess.CalledProcessError as e:
        print("Error during analysis:", e.output.decode('utf-8'))
        return

if __name__ == "__main__":
    firmware_file = "be550v1-firmware.bin"  # Replace with your actual firmware file if needed
    analyze_firmware(firmware_file)
