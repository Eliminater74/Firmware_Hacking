from Crypto.Cipher import AES, DES
import os

def aes_decrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)

def des_decrypt(data, key, iv):
    cipher = DES.new(key, DES.MODE_CBC, iv)
    return cipher.decrypt(data)

aes_section_path = "extracted_segments/AES_section.bin"
des_section_path = "extracted_segments/DES_section.bin"

with open(aes_section_path, "rb") as f:
    aes_data = f.read()

with open(des_section_path, "rb") as f:
    des_data = f.read()

dictionary_path = "dictionary.txt"  # Path to your dictionary file
with open(dictionary_path, "r") as f:
    keys = [line.strip() for line in f]

for key in keys:
    key_bytes = key.encode('utf-8').ljust(16, b'\x00')[:16]
    iv = b'\x00' * 16
    try:
        decrypted_data = aes_decrypt(aes_data, key_bytes, iv)
        if b'expected_pattern' in decrypted_data:
            with open("decrypted_AES_section.bin", "wb") as out:
                out.write(decrypted_data)
            print(f"AES Decryption successful with key: {key}")
            break
    except Exception:
        pass

    key_bytes = key.encode('utf-8').ljust(8, b'\x00')[:8]
    iv = b'\x00' * 8
    try:
        decrypted_data = des_decrypt(des_data, key_bytes, iv)
        if b'expected_pattern' in decrypted_data:
            with open("decrypted_DES_section.bin", "wb") as out:
                out.write(decrypted_data)
            print(f"DES Decryption successful with key: {key}")
            break
    except Exception:
        pass

print("Dictionary attack completed.")
