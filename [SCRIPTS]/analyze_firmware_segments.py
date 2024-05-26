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

def main():
    segments = ['segment_1_analysis.txt', 'segment_2_analysis.txt', 'segment_3_analysis.txt']

    for segment in segments:
        print(f"\nAnalyzing {segment}...\n")
        results = analyze_text_file(segment)

        print("Binwalk Results:")
        for match in results['binwalk']:
            print(f"Offset: {match[0]}, Description: {match[3]}")

        print("\nHexdump (first 40 lines):")
        hexdump_lines = results.get('hexdump', '').split('\n')[:40]
        for line in hexdump_lines:
            print(line)

        print("\nStrings Found:")
        for string in results.get('strings', []):
            print(string)

        print("\nEntropy:")
        print(results.get('entropy', 'N/A'))

if __name__ == "__main__":
    main()
