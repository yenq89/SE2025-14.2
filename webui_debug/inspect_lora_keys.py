# inspect_lora_keys.py
import sys
from safetensors import safe_open


if len(sys.argv) < 2:
    print("Usage: python inspect_lora_keys.py path/to/file.safetensors")
    sys.exit(1)


path = sys.argv[1]
print("Inspecting:", path)


with safe_open(path, framework="pt", device="cpu") as f:
    keys = list(f.keys())
print("Total keys:", len(keys))


for i, k in enumerate(keys[:200]):
    print(f"{i:04d}: {k}")


# Save keys to file
with open("lora_keys_list.txt", "w", encoding="utf-8") as fo:
    for k in keys:
        fo.write(k + "\n")
print("Saved full key list to lora_keys_list.txt")
