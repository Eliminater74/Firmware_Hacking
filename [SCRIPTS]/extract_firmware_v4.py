import subprocess
import os
import math

def save_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr

def calculate_entropy(data):
    byte_arr = list(data)
    file_size = len(byte_arr)
    freq_list = []

    for b in range(256):
        ctr = 0
        for byte in byte_arr:
            if byte == b:
                ctr += 1
        freq_list.append(float(ctr) / file_size)

    entropy = 0.0
    for freq in freq_list:
        if freq > 0:
            entropy = entropy + freq * math.log(freq, 2)
    entropy = -entropy

    return entropy

def analyze_segment(segment_file, segment_number):
    output = ""
    output += f"Analyzing {segment_file}...\n"
    binwalk_output = run_command(f"binwalk {segment_file}")
    output += binwalk_output

    if "gzip compressed data" in binwalk_output:
        output += "Detected gzip compressed data. Extracting...\n"
        run_command(f"dd if={segment_file} of={segment_file}.gzip bs=1 skip=0 count=$(stat -c %s {segment_file})")
        gzip_output = run_command(f"gzip -d {segment_file}.gzip")
        if gzip_output:
            output += f"Error during gzip extraction: {gzip_output}\n"

    if "bzip2 compressed data" in binwalk_output:
        output += "Detected bzip2 compressed data. Extracting...\n"
        run_command(f"dd if={segment_file} of={segment_file}.bzip2 bs=1 skip=0 count=$(stat -c %s {segment_file})")
        bzip2_output = run_command(f"bzip2 -d {segment_file}.bzip2")
        if bzip2_output:
            output += f"Error during bzip2 extraction: {bzip2_output}\n"

    # Hexdump analysis
    output += "Performing hexdump analysis...\n"
    hexdump_output = run_command(f"hexdump -C {segment_file} | head -n 40")
    output += f"Hexdump of {segment_file}:\n{hexdump_output}\n"

    # Strings analysis
    output += "Performing strings analysis...\n"
    strings_output = run_command(f"strings {segment_file}")
    output += f"Strings found in {segment_file}:\n{strings_output}\n"

    # Entropy analysis
    output += "Performing entropy analysis...\n"
    with open(segment_file, 'rb') as f:
        data = f.read()
    entropy = calculate_entropy(data)
    output += f"Entropy of {segment_file}: {entropy:.4f}\n"

    save_to_file(f"segment_{segment_number}_analysis.txt", output)

segments = ["segment_1.bin", "segment_2.bin", "segment_3.bin"]

for i, segment in enumerate(segments, start=1):
    analyze_segment(segment, i)
