# core/config.py
import os

# ====== CONFIG ======
BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", "runwayml/stable-diffusion-v1-5")

ROOT_IMAGE_DIR = os.getenv("ROOT_IMAGE_DIR",r"C:\Users\ssm_d\SE2025-14.2\software_product\images")

LORA_DIR = os.getenv(
    "LORA_DIR",
    r"C:\Users\ssm_d\SE2025-14.2\stable-diffusion-webui\models\Stable-diffusion"
)

REINIT_PIPE_ON_LOAD = os.getenv("REINIT_PIPE_ON_LOAD", "false").lower() == "true"
