import bz2

def extract_bzip2_data(segment_file, output_file):
    try:
        with open(segment_file, 'rb') as f:
            data = f.read()
            decompressed_data = bz2.decompress(data)
            with open(output_file, 'wb') as out:
                out.write(decompressed_data)
            print(f"Decompressed data written to {output_file}")
    except Exception as e:
        print(f"Error during decompression: {e}")

# Replace 'segment_2.bin' and 'segment_2_decompressed.bin' with the actual file names.
extract_bzip2_data('segment_2.bin', 'segment_2_decompressed.bin')
