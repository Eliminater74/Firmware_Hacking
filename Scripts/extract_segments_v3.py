#!/usr/bin/env python3

import os
import subprocess
import zlib
import bz2
import lzma

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

    for i, offset in enumerate(offsets):
        segment_file = os.path.join(output_dir, f"segment_{i}.bin")
        try:
            with open(segment_file, 'wb') as f:
                dd_command = ['dd', f'if={firmware_file}', f'of={segment_file}', f'skip={offset}', 'bs=1', 'count=1000000']
                print(f"Running command: {' '.join(dd_command)} for offset {offset}")
                subprocess.run(dd_command, stdout=f, stderr=subprocess.STDOUT, timeout=60)
        except subprocess.TimeoutExpired:
            print(f"dd operation for offset {offset} timed out.")
            continue
        except subprocess.CalledProcessError as e:
            print(f"Error running dd for offset {offset}:", e.output.decode('utf-8'))
            continue

        try:
            with open(segment_file, 'rb') as sf:
                data = sf.read()

                # Attempt zlib decompression
                if data[:2] in [b'\x78\x01', b'\x78\x9C', b'\x78\xDA']:
                    try:
                        print(f"Attempting to decompress {segment_file} with zlib...")
                        decompressed_data = zlib.decompress(data)
                        with open(os.path.join(output_dir, f"{segment_file}.decompressed.zlib"), 'wb') as df:
                            df.write(decompressed_data)
                        print(f"Decompressed data saved to {segment_file}.decompressed.zlib")
                        continue
                    except zlib.error as e:
                        print(f"Error decompressing {segment_file} with zlib: {e}")

                # Attempt bzip2 decompression
                try:
                    print(f"Attempting to decompress {segment_file} with bzip2...")
                    decompressed_data = bz2.decompress(data)
                    with open(os.path.join(output_dir, f"{segment_file}.decompressed.bzip2"), 'wb') as df:
                        df.write(decompressed_data)
                    print(f"Decompressed data saved to {segment_file}.decompressed.bzip2")
                    continue
                except OSError as e:
                    print(f"Error decompressing {segment_file} with bzip2: {e}")

                # Attempt lzma decompression
                try:
                    print(f"Attempting to decompress {segment_file} with lzma...")
                    decompressed_data = lzma.decompress(data)
                    with open(os.path.join(output_dir, f"{segment_file}.decompressed.lzma"), 'wb') as df:
                        df.write(decompressed_data)
                    print(f"Decompressed data saved to {segment_file}.decompressed.lzma")
                    continue
                except lzma.LZMAError as e:
                    print(f"Error decompressing {segment_file} with lzma: {e}")

                print(f"No valid compression format detected for {segment_file}")

        except Exception as e:
            print(f"Unexpected error handling {segment_file}: {e}")

if __name__ == "__main__":
    firmware_file = "be550v1-firmware.bin"  # Replace with your actual firmware file if needed
    extract_segments(firmware_file)
