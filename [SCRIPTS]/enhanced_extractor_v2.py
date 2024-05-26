import os
import subprocess
import shutil

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8')

def analyze_segment(segment_path):
    result = {}
    file_command = f"file {segment_path}"
    strings_command = f"strings {segment_path}"

    file_output, _ = run_command(file_command)
    strings_output, _ = run_command(strings_command)

    result['file'] = file_output.strip()
    result['strings'] = strings_output.strip()

    return result

def try_extraction_tools(segment_path, output_dir):
    tools = [
        f"binwalk -eM {segment_path} -C {output_dir}",
        f"7z x {segment_path} -o{output_dir}",
        f"tar -xf {segment_path} -C {output_dir}",
        f"dd if={segment_path} of={output_dir}/extracted_segment bs=512 skip=1"
    ]

    for tool in tools:
        stdout, stderr = run_command(tool)
        if os.path.exists(output_dir) and any(os.scandir(output_dir)):
            return stdout, stderr
    return None, None

def main():
    base_dir = '/home/eliminater74/Storage/firmware-analysis-toolkit'
    extract_dir = os.path.join(base_dir, 'extracted_segments')

    # Ensure the extract directory exists
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.bin'):
                file_path = os.path.join(root, file)
                output_dir = os.path.join(root, file + '_extracted')

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                print(f"Extracting {file_path} to {output_dir}")

                stdout, stderr = try_extraction_tools(file_path, output_dir)

                # Log the output of extraction tools for debugging
                log_file_path = os.path.join(output_dir, 'extraction.log')
                with open(log_file_path, 'w') as log_file:
                    if stdout:
                        log_file.write(stdout)
                    if stderr:
                        log_file.write(stderr)

                for extracted_root, extracted_dirs, extracted_files in os.walk(output_dir):
                    for extracted_file in extracted_files:
                        extracted_file_path = os.path.join(extracted_root, extracted_file)

                        # Check if the file is non-empty
                        if os.path.getsize(extracted_file_path) > 0:
                            result = analyze_segment(extracted_file_path)

                            result_file = os.path.join(extracted_root, extracted_file + '.analysis.txt')
                            with open(result_file, 'w') as rf:
                                rf.write(f"File analysis for {extracted_file_path}:\n")
                                rf.write(f"{result['file']}\n\n")
                                rf.write("Strings output:\n")
                                rf.write(result['strings'])

                            print(f"Analyzed {extracted_file_path}, results saved to {result_file}")
                        else:
                            print(f"Skipped empty file {extracted_file_path}")

if __name__ == '__main__':
    main()
