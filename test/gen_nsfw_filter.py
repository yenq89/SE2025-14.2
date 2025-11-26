# gen_nsfw_filter.py có chức năng kiểm tra kết quả đầu ra của toàn bộ dữ liệu
# và lưu lại các caption gặp vấn đề NSFW vào file metadata.jsonl

import os
import json
from pathlib import Path
from tqdm import tqdm
import torch
from diffusers import StableDiffusionPipeline

# ====== Cấu hình ====== #
ROOT = r"C:\Users\ssm_d\SE2025-14.2"

METADATA = os.path.join(ROOT, "data", "ghibli", "train", "metadata.jsonl")

NSFW_DIR = os.path.join(ROOT, "test", "nsfw_data2")                    # Lưu Caption dính NSFW (đã đổi địa chỉ đích)
os.makedirs(NSFW_DIR, exist_ok=True)
NSFW_METADATA = os.path.join(NSFW_DIR, "metadata.jsonl")

# 
MODEL_FOLDER = os.path.join(ROOT, "model", "ghibli_checkpoint", "checkpoint-17000")
LORA_FILE = os.path.join(MODEL_FOLDER, "pytorch_lora_weights.safetensors")
# ======================= #


def load_pipeline():
    print("Loading Stable Diffusion base model...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16
    ).to("cuda")
    pipe.safety_checker = lambda images, clip_input: (images, [False] * len(images))

    # Load LoRA nếu có
    if os.path.exists(LORA_FILE):
        print("Loading LoRA:", LORA_FILE)
        try:
            pipe.load_lora_weights(LORA_FILE)
        except:
            pipe.unet.load_attn_procs(LORA_FILE)
    return pipe


def main():
    pipe = load_pipeline()

    print("\nĐọc metadata:", METADATA)
    lines = open(METADATA, "r", encoding="utf-8").read().splitlines()

    nsfw_list = []  # danh sách caption bị dính
    out_f = open(NSFW_METADATA, "a", encoding="utf-8")

    for line in tqdm(lines):
        item = json.loads(line)
        caption = item.get("text", "").strip()

        try:
            result = pipe(caption, num_inference_steps=30, guidance_scale=7.5)
            flags = getattr(result, "nsfw_content_detected", None)

            if flags and any(flags):
                nsfw_list.append(caption)
                out_f.write(line + "\n")
                print("NSFW:", caption)

        except Exception as e:
            print("ERROR:", e)
            nsfw_list.append(caption)
            out_f.write(line + "\n")

    out_f.close()

    print("\n===== KẾT QUẢ CUỐI =====")
    print("Số caption bị NSFW:", len(nsfw_list))
    for cap in nsfw_list:
        print("-", cap)


if __name__ == "__main__":
    main()