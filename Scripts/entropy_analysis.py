import os
import math
from collections import Counter

def calculate_entropy(data):
    if not data:
        return 0
    entropy = 0
    counter = Counter(data)
    for count in counter.values():
        p_x = count / len(data)
        entropy += - p_x * math.log2(p_x)
    return entropy

firmware_path = "be550v1-firmware.bin"
with open(firmware_path, "rb") as f:
    firmware_data = f.read()

window_size = 4096
step_size = 4096
results = []
for i in range(0, len(firmware_data) - window_size + 1, step_size):
    window = firmware_data[i:i + window_size]
    entropy = calculate_entropy(window)
    results.append((i, entropy))

with open("entropy_analysis.txt", "w") as out:
    for position, entropy in results:
        out.write(f"{position}: {entropy}\n")

print("Entropy analysis completed. Check 'entropy_analysis.txt' for the results.")
