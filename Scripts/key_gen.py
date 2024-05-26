import itertools
import string

# Generate all possible combinations of a certain length
key_length = 16
charset = string.ascii_letters + string.digits  # Example charset

def generate_keys():
    for key_tuple in itertools.product(charset, repeat=key_length):
        yield ''.join(key_tuple).encode('utf-8')

# Example usage of key generator
for key in generate_keys():
    print(key)
