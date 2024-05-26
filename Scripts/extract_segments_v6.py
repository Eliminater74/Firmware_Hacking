#!/usr/bin/env python3

import os
import subprocess
import zlib
import bz2
import lzma
import gzip
from lz4.frame import decompress as lz4_decompress

# Known file signatures and their corresponding decompression methods
FILE_SIGNATURES = {
    b'\x1F\x8B': 'gzip',
    b'\x42\x5A\x68': 'bzip2',
    b'\xFD\x37\x7A\x58\x5A': 'xz',
    b'\x28\xB5\x2F\xFD': 'lz4',
    b'\x78\x01': 'zlib',
    b'\x78\x9C': 'zlib',
    b'\x78\xDA': 'zlib',
    # Add more signatures if needed
}

def decompress_data(data, signature):
    try:
        if signature == 'gzip':
            return gzip.decompress(data)
        elif signature == 'bzip2':
            return bz2.decompress(data)
        elif signature == 'xz':
            return lzma.decompress(data)
        elif signature == 'lz4':
            return lz4_decompress(data)
        elif signature == 'zlib':
            return zlib.decompress(data)
    except Exception as e:
        print(f"Error decompressing data with {signature}: {e}")
    return None

def extract_segments(firmware_file):
    output_dir = "extracted"
    os.makedirs(output_dir, exist_ok=True)

    try:
        binwalk_output = subprocess.check_output(['binwalk', firmware_file], stderr=subprocess.STDOUT, timeout=60).decode('utf-8')
    except subprocess.TimeoutExpired:
        print("Binwalk operation timed out.")
        return
    except subprocess.CalledProcessError as e:
        print("Error running binwalk:", e.output.decode('utf-8'))
        return

    print("Binwalk output:")
    print(binwalk_output)

    offsets = []
    for line in binwalk_output.splitlines():
        if "compressed data" in line:
            offset = int(line.split()[0])
            offsets.append(offset)

    print("Offsets found:", offsets)

    failed_segments = []

    for i, offset in enumerate(offsets):
        segment_dir = os.path.join(output_dir, f"segment_{i}")
        os.makedirs(segment_dir, exist_ok=True)
        segment_file = os.path.join(segment_dir, f"segment_{i}.bin")
        try:
            dd_command = ['dd', f'if={firmware_file}', f'of={segment_file}', f'skip={offset}', 'bs=1', 'count=1000000']
            print(f"Running command: {' '.join(dd_command)} for offset {offset}")
            subprocess.run(dd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        except subprocess.TimeoutExpired:
            print(f"dd operation for offset {offset} timed out.")
            failed_segments.append((segment_file, "dd timeout"))
            continue
        except subprocess.CalledProcessError as e:
            print(f"Error running dd for offset {offset}:", e.output.decode('utf-8'))
            failed_segments.append((segment_file, "dd error"))
            continue

        try:
            with open(segment_file, 'rb') as sf:
                data = sf.read()

                decompressed = False

                for signature, decompressor in FILE_SIGNATURES.items():
                    if data.startswith(signature):
                        print(f"Attempting to decompress {segment_file} with {decompressor}...")
                        decompressed_data = decompress_data(data, decompressor)
                        if decompressed_data:
                            with open(os.path.join(segment_dir, f"{segment_file}.decompressed.{decompressor}"), 'wb') as df:
                                df.write(decompressed_data)
                            print(f"Decompressed data saved to {segment_file}.decompressed.{decompressor}")
                            decompressed = True
                            break

                if not decompressed:
                    print(f"No valid compression format detected for {segment_file}")
                    failed_segments.append((segment_file, "no valid compression format"))

        except Exception as e:
            print(f"Unexpected error handling {segment_file}: {e}")
            failed_segments.append((segment_file, "unexpected error"))

    # Log failed segments
    with open(os.path.join(output_dir, "failed_segments.log"), 'w') as log_file:
        for segment, reason in failed_segments:
            log_file.write(f"{segment}: {reason}\n")

if __name__ == "__main__":
    firmware_file = "be550v1-firmware.bin"  # Replace with your actual firmware file if needed
    extract_segments(firmware_file)
