import os
import subprocess

def extract_segments(firmware_file):
    # Run binwalk to get the list of segments
    binwalk_output = subprocess.check_output(['binwalk', firmware_file]).decode('utf-8')
    print("Binwalk output:")
    print(binwalk_output)

    # Parse binwalk output to get offsets
    offsets = []
    for line in binwalk_output.splitlines():
        if "Raw deflate compression stream" in line:
            offset = int(line.split()[0])
            offsets.append(offset)

    print("Offsets found:", offsets)

    # Extract segments using dd
    for i, offset in enumerate(offsets):
        segment_file = f"segment_{i}.bin"
        with open(segment_file, 'wb') as f:
            dd_command = ['dd', f'if={firmware_file}', f'of={segment_file}', f'skip={offset}', 'bs=1', 'count=1000000']
            print("Running command:", ' '.join(dd_command))
            subprocess.run(dd_command, stdout=f)

        # Attempt to decompress the segment
        try:
            print(f"Attempting to decompress {segment_file}...")
            subprocess.run(['gzip', '-d', segment_file])
        except Exception as e:
            print(f"Error decompressing {segment_file}: {e}")

if __name__ == "__main__":
    firmware_file = "be550v1-firmware.bin"  # Replace with your actual firmware file
    extract_segments(firmware_file)
