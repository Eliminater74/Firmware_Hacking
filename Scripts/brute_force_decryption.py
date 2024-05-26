from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import itertools
import string

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

firmware_path = "be550v1-firmware.bin"
iv = b'\x00' * 16  # Adjust if you know the correct IV

# Example charset and key length
charset = string.ascii_letters + string.digits  # Charset can be modified
key_length = 16  # AES key length can be 16, 24, or 32 bytes

with open(firmware_path, "rb") as f:
    encrypted_data = f.read()

for key in generate_keys(charset, key_length):
    decrypted_data = aes_decrypt(encrypted_data, key, iv)
    if decrypted_data and b'fw-type' in decrypted_data:  # Check for a known pattern
        with open("decrypted_firmware.bin", "wb") as out:
            out.write(decrypted_data)
        print(f"AES Decryption successful with key: {key.decode('utf-8')}")
        break
    else:
        print(f"Failed with key: {key.decode('utf-8')}")

print("Decryption attempt completed.")
