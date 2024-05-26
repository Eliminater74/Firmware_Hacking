import os
import subprocess
import shutil

def run_binwalk(file_path, output_dir):
    """Run binwalk to extract files from the given file and save to the output directory."""
    print(f"[+] Running binwalk on {file_path}")
    try:
        subprocess.run(["binwalk", "-e", "--directory", output_dir, file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Binwalk extraction failed for {file_path}: {e}")

def recursively_extract(directory):
    """Recursively extract all .bin files in the given directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".bin"):
                file_path = os.path.join(root, file)
                output_dir = os.path.join(root, f"{file}_extracted")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                run_binwalk(file_path, output_dir)

                # Recursively extract newly extracted files
                recursively_extract(output_dir)

def main(firmware_path):
    initial_output_dir = 'initial_extracted'
    if os.path.exists(initial_output_dir):
        shutil.rmtree(initial_output_dir)
    os.makedirs(initial_output_dir)

    run_binwalk(firmware_path, initial_output_dir)
    recursively_extract(initial_output_dir)

if __name__ == "__main__":
    firmware_path = 'firmware.bin'  # Path to your firmware file
    main(firmware_path)
