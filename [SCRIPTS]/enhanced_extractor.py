import os
import subprocess

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    return stdout, stderr

def analyze_segment(segment_path):
    result = {}
    file_command = f"file {segment_path}"
    strings_command = f"strings {segment_path}"

    file_output, _ = run_command(file_command)
    strings_output, _ = run_command(strings_command)

    result['file'] = file_output.decode('utf-8').strip()
    result['strings'] = strings_output.decode('utf-8').strip()

    return result

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
                binwalk_command = f"binwalk -eM {file_path} -C {output_dir}"
                stdout, stderr = run_command(binwalk_command)

                # Log the output of binwalk for debugging
                with open(f"{output_dir}/binwalk.log", 'w') as log_file:
                    log_file.write(stdout.decode('utf-8'))
                    log_file.write(stderr.decode('utf-8'))

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
