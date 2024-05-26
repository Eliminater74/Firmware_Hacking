import struct
import os

# Known file signatures
SIGNATURES = {
    b'\x1F\x8B\x08': 'gzip',
    b'\x50\x4B\x03\x04': 'zip',
    b'\x42\x5A\x68': 'bzip2',
    b'\x37\x7A\xBC\xAF\x27\x1C': '7z',
    b'\xFD\x37\x7A\x58\x5A\x00': 'xz',
    b'\x1F\x9D': 'compress',
    b'\x53\x51\x48\x33': 'squashfs',
    b'\x68\x73\x71\x73': 'cramfs',
    b'\x55\xAA': 'DOS_MBR_boot_sector',
    b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'MS_Office_Document',
    b'\x4D\x5A': 'MZ_Executable',
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG_Image',
}

def find_signatures(data):
    segments = []
    for signature, name in SIGNATURES.items():
        offset = data.find(signature)
        while offset != -1:
            segments.append((offset, name, signature))
            offset = data.find(signature, offset + 1)
    return segments

def extract_segments(firmware_path, segments):
    with open(firmware_path, 'rb') as f:
        data = f.read()

    output_dir = 'extracted_segments'
    os.makedirs(output_dir, exist_ok=True)

    for idx, (offset, name, signature) in enumerate(segments):
        next_offset = len(data)
        for next_offset_candidate, _, _ in segments:
            if next_offset_candidate > offset:
                next_offset = next_offset_candidate
                break

        segment_data = data[offset:next_offset]
        sanitized_name = name.replace('/', '_').replace(' ', '_')
        segment_path = os.path.join(output_dir, f'segment_{idx}_{sanitized_name}.bin')
        with open(segment_path, 'wb') as out:
            out.write(segment_data)
            print(f"[+] Extracted {name} segment to {segment_path} (offset: {offset})")

def main(firmware_path):
    with open(firmware_path, 'rb') as f:
        data = f.read()

    segments = find_signatures(data)
    if not segments:
        print("[!] No known file signatures found in the firmware.")
        return

    for offset, name, signature in segments:
        print(f"[+] Found {name} signature at offset {offset}")

    extract_segments(firmware_path, segments)

if __name__ == "__main__":
    firmware_path = 'firmware.bin'
    main(firmware_path)
