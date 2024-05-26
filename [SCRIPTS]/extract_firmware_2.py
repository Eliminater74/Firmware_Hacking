import os
import subprocess
import binwalk

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode(), result.stderr.decode()

def identify_and_extract(segment_file):
    print(f"Analyzing {segment_file}...")

    # Running binwalk to identify known patterns
    binwalk_result = binwalk.scan(segment_file, signature=True, quiet=True)
    for module in binwalk_result:
        for result in module.results:
            print(f"Found {result.description} at offset {result.offset}")

    # Common decompression tools and their signatures
    decompressors = {
        'gzip': ('gzip', b'\x1f\x8b\x08'),
        'bzip2': ('bzip2', b'\x42\x5a\x68'),
        'xz': ('xz', b'\xfd\x37\x7a\x58\x5a\x00'),
        'lzma': ('lzma', b'\x5d\x00\x00\x80\x00'),
    }

    extracted_files = []

    for name, (command, signature) in decompressors.items():
        with open(segment_file, 'rb') as f:
            data = f.read()
            if signature in data:
                output_file = f"{segment_file}.{name}"
                with open(output_file, 'wb') as out_f:
                    out_f.write(data)
                print(f"Detected {name} compressed data. Extracting to {output_file}...")
                extract_command = f"{command} -d {output_file}"
                stdout, stderr = run_command(extract_command)
                if stderr:
                    print(f"Error during {name} extraction: {stderr}")
                else:
                    extracted_files.append(output_file)
                    print(f"Extracted {name} data to {output_file}")

    if not extracted_files:
        print(f"No known compression formats detected in {segment_file}.")

if __name__ == "__main__":
    segments = ['segment_1.bin', 'segment_2.bin', 'segment_3.bin']
    for segment in segments:
        identify_and_extract(segment)
