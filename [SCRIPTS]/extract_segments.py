import os

# Define known file signatures (magic numbers) and their descriptions
SIGNATURES = {
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'png',
    b'\xFF\xD8\xFF': 'jpeg',
    b'\x50\x4B\x03\x04': 'zip',
    b'\x7F\x45\x4C\x46': 'elf',
    b'\x1F\x8B': 'gzip',
    b'\x42\x5A\x68': 'bzip2',
    b'\x37\x7A\xBC\xAF\x27\x1C': '7z',
    b'\xFD\x37\x7A\x58\x5A\x00': 'xz',
    b'\x1F\x9D': 'compress',
    b'\x4D\x5A': 'mz_executable',
    b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'ms_office_document',
}

def find_signatures(data):
    segments = []
    for signature, description in SIGNATURES.items():
        offset = data.find(signature)
        while offset != -1:
            segments.append((offset, description, signature))
            offset = data.find(signature, offset + 1)
    return segments

def extract_segments(file_path, segments, output_dir):
    with open(file_path, 'rb') as f:
        data = f.read()

    os.makedirs(output_dir, exist_ok=True)

    for idx, (offset, description, signature) in enumerate(segments):
        next_offset = len(data)
        for next_offset_candidate, _, _ in segments:
            if next_offset_candidate > offset:
                next_offset = next_offset_candidate
                break

        segment_data = data[offset:next_offset]
        segment_path = os.path.join(output_dir, f'segment_{idx:03d}_{description}.bin')
        with open(segment_path, 'wb') as out:
            out.write(segment_data)
            print(f"[+] Extracted {description} segment to {segment_path} (offset: {offset})")

def analyze_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    segments = find_signatures(data)
    if not segments:
        print(f"[!] No known file signatures found in {file_path}.")
        return

    for offset, description, signature in segments:
        print(f"[+] Found {description} signature at offset {offset}")

    output_dir = f"{os.path.basename(file_path)}_extracted"
    extract_segments(file_path, segments, output_dir)

def main():
    files_to_analyze = [
        'scalpel_output2/fws-20-0/00000000.fws',
        'scalpel_output2/fws-20-0/00000001.fws',
        'scalpel_output2/wpc-28-0/00000002.wpc',
        'scalpel_output2/wpc-28-0/00000003.wpc',
    ]

    for file_path in files_to_analyze:
        if os.path.isfile(file_path):
            print(f"\nAnalyzing {file_path}...")
            analyze_file(file_path)
        else:
            print(f"[!] File not found: {file_path}")

if __name__ == "__main__":
    main()
