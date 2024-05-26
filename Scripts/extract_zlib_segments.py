#!/usr/bin/env python3

import os
import subprocess
import zlib
import binascii

def extract_segments(firmware_file):
    # Run binwalk to get the list of segments
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

    # Parse binwalk output to get offsets
    offsets = []
    for line in binwalk_output.splitlines():
        if "Zlib compressed data" in line:
            offset = int(line.split()[0])
            offsets.append(offset)

    print("Offsets found:", offsets)

    # Extract segments using dd
    for i, offset in enumerate(offsets):
        segment_file = f"segment_{i}.bin"
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

        # Attempt to decompress the segment using zlib
        try:
            print(f"Attempting to decompress {segment_file}...")
            with open(segment_file, 'rb') as sf:
                data = sf.read()
                # Check for zlib header (0x78, 0x01 to 0x78, 0x9C are common valid headers)
                if data[:2] in [b'\x78\x01', b'\x78\x9C', b'\x78\xDA']:
                    decompressor = zlib.decompressobj()
                    decompressed_data = decompressor.decompress(data)
                    decompressed_data += decompressor.flush()
                    with open(f"{segment_file}.decompressed", 'wb') as df:
                        df.write(decompressed_data)
                    print(f"Decompressed data saved to {segment_file}.decompressed")
                else:
                    print(f"Invalid zlib header for {segment_file}")
        except zlib.error as e:
            print(f"Error decompressing {segment_file}: {e}")
        except Exception as e:
            print(f"Unexpected error decompressing {segment_file}: {e}")

if __name__ == "__main__":
    firmware_file = "be550v1-firmware.bin"  # Replace with your actual firmware file if needed
    extract_segments(firmware_file)
