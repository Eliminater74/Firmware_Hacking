#!/bin/bash

EXTRACT_DIR="$HOME/Storage/firmware-analysis-toolkit"

# Extract GZIP files
find "$EXTRACT_DIR" -type f -name "*.gzip.bin" | while read -r file; do
    output_file="${file%.gzip.bin}.extracted"
    gunzip -c "$file" > "$output_file"
    echo "[+] Extracted $file to $output_file"
done

# Inspect executable files
find "$EXTRACT_DIR" -type f -name "*mz_executable.bin" | while read -r file; do
    echo "Inspecting $file"
    file "$file"
    strings "$file" | less
done
