#!/usr/bin/env python3

import os
import subprocess
import zlib
import bz2
import lzma
import gzip
from lz4.frame import decompress as lz4_decompress

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
        segment_file = os.path.join(output_dir, f"segment_{i}.bin")
        try:
            with open(segment_file, 'wb') as f:
                dd_command = ['dd', f'if={firmware_file}', f'of={segment_file}', f'skip={offset}', 'bs=1', 'count=1000000']
                print(f"Running command: {' '.join(dd_command)} for offset {offset}")
                subprocess.run(dd_command, stdout=f, stderr=subprocess.STDOUT, timeout=60)
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

                # Attempt decompression for various formats based on file signatures
                if data.startswith(b'\x1F\x8B'):
                    try:
                        print(f"Attempting to decompress {segment_file} with gzip...")
                        decompressed_data = gzip.decompress(data)
                        with open(os.path.join(output_dir, f"{segment_file}.decompressed.gzip"), 'wb') as df:
                            df.write(decompressed_data)
                        print(f"Decompressed data saved to {segment_file}.decompressed.gzip")
                        decompressed = True
                    except OSError as e:
                        print(f"Error decompressing {segment_file} with gzip: {e}")

                elif data.startswith(b'\x42\x5A\x68'):
                    try:
                        print(f"Attempting to decompress {segment_file} with bzip2...")
                        decompressed_data = bz2.decompress(data)
                        with open(os.path.join(output_dir, f"{segment_file}.decompressed.bzip2"), 'wb') as df:
                            df.write(decompressed_data)
                        print(f"Decompressed data saved to {segment_file}.decompressed.bzip2")
                        decompressed = True
                    except OSError as e:
                        print(f"Error decompressing {segment_file} with bzip2: {e}")

                elif data.startswith(b'\xFD\x37\x7A\x58\x5A'):
                    try:
                        print(f"Attempting to decompress {segment_file} with xz...")
                        decompressed_data = lzma.decompress(data)
                        with open(os.path.join(output_dir, f"{segment_file}.decompressed.xz"), 'wb') as df:
                            df.write(decompressed_data)
                        print(f"Decompressed data saved to {segment_file}.decompressed.xz")
                        decompressed = True
                    except lzma.LZMAError as e:
                        print(f"Error decompressing {segment_file} with xz: {e}")

                elif data.startswith(b'\x28\xB5\x2F\xFD'):
                    try:
                        print(f"Attempting to decompress {segment_file} with lz4...")
                        decompressed_data = lz4_decompress(data)
                        with open(os.path.join(output_dir, f"{segment_file}.decompressed.lz4"), 'wb') as df:
                            df.write(decompressed_data)
                        print(f"Decompressed data saved to {segment_file}.decompressed.lz4")
                        decompressed = True
                    except Exception as e:
                        print(f"Error decompressing {segment_file} with lz4: {e}")

                elif data.startswith(b'\x78\x01') or data.startswith(b'\x78\x9C') or data.startswith(b'\x78\xDA'):
                    try:
                        print(f"Attempting to decompress {segment_file} with zlib...")
                        decompressed_data = zlib.decompress(data)
                        with open(os.path.join(output_dir, f"{segment_file}.decompressed.zlib"), 'wb') as df:
                            df.write(decompressed_data)
                        print(f"Decompressed data saved to {segment_file}.decompressed.zlib")
                        decompressed = True
                    except zlib.error as e:
                        print(f"Error decompressing {segment_file} with zlib: {e}")

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
