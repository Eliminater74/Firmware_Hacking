#!/bin/bash

EXTRACT_DIR="$HOME/Storage/firmware-analysis-toolkit"

# Extract GZIP files
find "$EXTRACT_DIR" -type f -name "*.gzip.bin" | while read -r file; do
    output_file="${file%.gzip.bin}.extracted"
    gunzip -c "$file" > "$output_file"
    echo "[+] Extracted $file to $output_file"
done

# Create directories for categorized files
mkdir -p "$EXTRACT_DIR/extracted_files"
mkdir -p "$EXTRACT_DIR/inspections"

# Inspect executable files
find "$EXTRACT_DIR" -type f -name "*mz_executable.bin" | while read -r file; do
    echo "Inspecting $file" | tee -a "$EXTRACT_DIR/inspections/executable_inspection.log"
    file "$file" | tee -a "$EXTRACT_DIR/inspections/executable_inspection.log"
    strings "$file" > "$EXTRACT_DIR/inspections/$(basename "$file").strings"
done

# Inspect all extracted files
find "$EXTRACT_DIR" -type f -name "*.extracted" | while read -r file; do
    echo "Inspecting $file" | tee -a "$EXTRACT_DIR/inspections/extracted_files_inspection.log"
    file "$file" | tee -a "$EXTRACT_DIR/inspections/extracted_files_inspection.log"
    strings "$file" > "$EXTRACT_DIR/inspections/$(basename "$file").strings"
done

echo "Inspection complete. Results saved in $EXTRACT_DIR/inspections"
