import re

def analyze_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    analysis_results = {}

    # Binwalk output analysis
    binwalk_matches = re.findall(r"(\d+)\s+(\d+)\s+(.*?)\s+(.*)", content)
    analysis_results['binwalk'] = binwalk_matches

    # Hexdump analysis
    hexdump_section = re.search(r"Hexdump of .*?bin:(.*?)Strings found", content, re.DOTALL)
    if hexdump_section:
        analysis_results['hexdump'] = hexdump_section.group(1).strip()

    # Strings analysis
    strings_section = re.search(r"Strings found in .*?bin:(.*?)Entropy of", content, re.DOTALL)
    if strings_section:
        analysis_results['strings'] = strings_section.group(1).strip().split("\n")

    # Entropy analysis
    entropy_match = re.search(r"Entropy of .*?bin: (.*?)\n", content)
    if entropy_match:
        analysis_results['entropy'] = float(entropy_match.group(1))

    return analysis_results

def detect_file_signatures(strings):
    file_signatures = {
        'JPEG': re.compile(r'\xFF\xD8\xFF'),
        'PNG': re.compile(r'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'),
        'GIF': re.compile(r'\x47\x49\x46\x38'),
        'ZIP': re.compile(r'\x50\x4B\x03\x04'),
        'RAR': re.compile(r'\x52\x61\x72\x21\x1A\x07\x00'),
        'GZIP': re.compile(r'\x1F\x8B'),
        'BZ2': re.compile(r'\x42\x5A\x68'),
        '7z': re.compile(r'\x37\x7A\xBC\xAF\x27\x1C')
    }

    detected_signatures = {}
    for line in strings:
        for signature, pattern in file_signatures.items():
            if pattern.search(line):
                if signature not in detected_signatures:
                    detected_signatures[signature] = []
                detected_signatures[signature].append(line)

    return detected_signatures

def main():
    segments = ['segment_1_analysis.txt', 'segment_2_analysis.txt', 'segment_3_analysis.txt']

    for segment in segments:
        output_file = f"{segment}_output.txt"
        with open(output_file, 'w') as out_file:
            out_file.write(f"\nAnalyzing {segment}...\n\n")
            results = analyze_text_file(segment)

            out_file.write("Binwalk Results:\n")
            for match in results['binwalk']:
                out_file.write(f"Offset: {match[0]}, Description: {match[3]}\n")

            out_file.write("\nHexdump (first 40 lines):\n")
            hexdump_lines = results.get('hexdump', '').split('\n')[:40]
            for line in hexdump_lines:
                out_file.write(line + "\n")

            out_file.write("\nStrings Found:\n")
            for string in results.get('strings', []):
                out_file.write(string + "\n")

            out_file.write("\nFile Signatures Detected in Strings:\n")
            signatures = detect_file_signatures(results.get('strings', []))
            for signature, lines in signatures.items():
                out_file.write(f"{signature} found in lines:\n")
                for line in lines:
                    out_file.write(line + "\n")

            out_file.write("\nEntropy:\n")
            out_file.write(str(results.get('entropy', 'N/A')) + "\n")

        print(f"Analysis of {segment} written to {output_file}")

if __name__ == "__main__":
    main()
