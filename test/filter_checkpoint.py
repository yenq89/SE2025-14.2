from diffusers import StableDiffusionPipeline
import torch
import os
import re

# ====== CONFIG ======
# ROOT = r"C:\Users\ssm_d\SE2025-14.2\test\images\filter_checkpoint"

# LORA_PATH = r"C:\Users\ssm_d\SE2025-14.2\model\ghibli_checkpoint_data_v4.3\checkpoint-7000\pytorch_lora_weights.safetensors"
# MODEL_ID = "runwayml/stable-diffusion-v1-5"
ROOT_SAVE = r"C:\Users\ssm_d\SE2025-14.2\test\images\filter_checkpoint"
MODEL_ROOT = r"C:\Users\ssm_d\SE2025-14.2\model"
DATA_VERSION = "ghibli_checkpoint_data_v5.1"
MODEL_ID = "runwayml/stable-diffusion-v1-5"

DEVICE = "cuda:1"

# #  Lấy 2 folder cuối:
# parent_dir = os.path.dirname(LORA_PATH)

# MODEL_NAME = os.path.join(
#     os.path.basename(os.path.dirname(parent_dir)),  
#     os.path.basename(parent_dir)                   
# )

# # Chuẩn hoá tên folder (tránh tạo thư mục lồng nhau)
# MODEL_NAME = MODEL_NAME.replace("\\", "_")

# SAVE_DIR = os.path.join(ROOT, MODEL_NAME)
# os.makedirs(SAVE_DIR, exist_ok=True)

# ====== LOAD MODEL (1 LẦN) ======
# pipe = StableDiffusionPipeline.from_pretrained(
#     MODEL_ID,
#     torch_dtype=torch.float16,
#     safety_checker=None,
#     requires_safety_checker=False,
#     local_files_only=True
# )

# pipe = pipe.to("cuda")

# pipe.load_lora_weights(LORA_PATH)

# ====== PROMPTS (20 PROMPT – CHỈ NGƯỜI) ======
prompts = [
    "Ghibli style, a young woman with short brown hair, soft lighting, calm expression, indoor scene",
    "Ghibli style, a teenage girl with long black hair, gentle smile, clean background",
    "Ghibli style, a young man with glasses, casual outfit, warm colors, portrait",
    "Ghibli style, a girl sitting on a chair, relaxed posture, minimal background",
    "Ghibli style, a teenage boy looking forward, soft facial features",
    "Ghibli style, a young woman with shoulder-length hair, cozy indoor lighting",
    "Ghibli style, a teenage boy with messy hair, calm eyes, studio background",
    "Ghibli style, a girl holding a book, peaceful expression",
    "Ghibli style, a young adult woman, side profile, soft shadows",
    "Ghibli style, a portrait of a person, gentle colors, simple background",

    "Ghibli style, a young woman wearing a light sweater, neutral background",
    "Ghibli style, a teenage girl with tied hair, soft smile",
    "Ghibli style, a young man with short hair, calm expression",
    "Ghibli style, a girl standing still, pastel color palette",
    "Ghibli style, a boy sitting indoors, warm light",
    "Ghibli style, a young woman portrait, clean composition",
    "Ghibli style, a teenage boy portrait, soft lighting",
    "Ghibli style, a girl looking slightly to the side, gentle mood",
    "Ghibli style, a young adult person, close-up portrait",
    "Ghibli style, a calm human portrait, simple indoor background"
]

# ======================
# FIND ALL CHECKPOINTS
# ======================
data_dir = os.path.join(MODEL_ROOT, DATA_VERSION)

checkpoint_dirs = [
    d for d in os.listdir(data_dir)
    if os.path.isdir(os.path.join(data_dir, d)) and d.startswith("checkpoint-")
]

# sort checkpoint theo step số
checkpoint_dirs.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))

print(f"🔍 Found {len(checkpoint_dirs)} checkpoints in {DATA_VERSION}")

# ======================
# LOAD BASE MODEL (1 LẦN)
# ======================
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    safety_checker=None,
    requires_safety_checker=False,
    local_files_only=True
).to(DEVICE)

pipe.enable_attention_slicing()

# ======================
# LOOP QUA TỪNG CHECKPOINT
# ======================
for ckpt in checkpoint_dirs:
    print(f"\n🚀 Testing {ckpt}")

    ckpt_path = os.path.join(data_dir, ckpt, "pytorch_lora_weights.safetensors")

    if not os.path.exists(ckpt_path):
        print(f"⚠️ Missing LoRA file in {ckpt}, skip")
        continue

    # load LoRA
    pipe.unload_lora_weights()
    pipe.load_lora_weights(ckpt_path)

    # output dir
    save_dir = os.path.join(ROOT_SAVE, DATA_VERSION, ckpt)
    os.makedirs(save_dir, exist_ok=True)

    # generate images
    with torch.inference_mode():
        for idx, prompt in enumerate(prompts, start=1):
            image = pipe(
                prompt,
                num_inference_steps=30,
                guidance_scale=7.5
            ).images[0]

            image.save(os.path.join(save_dir, f"img_{idx:02d}.png"))

    print(f"✅ Done {ckpt}")

print("\n🎉 ALL CHECKPOINTS TESTED SUCCESSFULLY")
# # ====== GENERATE IMAGES ======
# for idx, prompt in enumerate(prompts, start=1):
#     image = pipe(
#         prompt,
#         num_inference_steps=30,
#         guidance_scale=7.5
#     ).images[0]

#     image_name = f"img_{idx:02d}.png"
#     image.save(os.path.join(SAVE_DIR, image_name))
#     print(f"Saved: {image_name}")

# print(f"✅ Done generating {len(prompts)} images for model: {MODEL_NAME}")


