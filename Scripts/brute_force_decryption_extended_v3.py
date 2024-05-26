from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import itertools
import string
import multiprocessing
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def aes_decrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data, AES.block_size)  # Pad data to be 16-byte aligned
    decrypted_data = cipher.decrypt(padded_data)
    try:
        return unpad(decrypted_data, AES.block_size)
    except ValueError:
        return None

def generate_keys(charset, key_length):
    for key_tuple in itertools.product(charset, repeat=key_length):
        yield ''.join(key_tuple).encode('utf-8')

def worker(key_chunk):
    iv = b'\x00' * 16
    with open(firmware_path, "rb") as f:
        encrypted_data = f.read()
    for i, key in enumerate(key_chunk):
        decrypted_data = aes_decrypt(encrypted_data, key, iv)
        if decrypted_data and b'fw-type' in decrypted_data:
            with open("decrypted_firmware.bin", "wb") as out:
                out.write(decrypted_data)
            return f"AES Decryption successful with key: {key.decode('utf-8')}"
        if i % 1000 == 0:  # Print progress every 1000 keys
            logging.info(f"Checked {i} keys in this chunk...")
    return None

def generate_key_chunks(charset, key_length, num_chunks):
    all_keys = list(generate_keys(charset, key_length))
    chunk_size = len(all_keys) // num_chunks
    return [all_keys[i:i + chunk_size] for i in range(0, len(all_keys), chunk_size)]

firmware_path = "be550v1-firmware.bin"
charset = string.ascii_letters + string.digits  # Charset can be modified
key_length = 16  # AES key length can be 16, 24, or 32 bytes

num_workers = multiprocessing.cpu_count()
key_chunks = generate_key_chunks(charset, key_length, num_workers)

with multiprocessing.Pool(num_workers) as pool:
    results = pool.map(worker, key_chunks)
    for result in results:
        if result:
            print(result)
            break

print("Decryption attempt completed.")
