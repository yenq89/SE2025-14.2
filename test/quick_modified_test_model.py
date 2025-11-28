# File kiểm tra data trước khi có giải pháp fix bug
# Kết quả kỳ vọng của file **quick_modified_test_model.py** là nhập đầu vào, 
# chạy qua 1 trong 2 mô hình được huấn luyện LoRA từ dữ liệu, nhận kết quả đầu ra là ảnh bình thường hoặc ảnh đen nếu dính NSFW.

from diffusers import StableDiffusionPipeline
import torch
import os

ROOT = r"C:\Users\ssm_d\SE2025-14.2"

## Không phải model hoàn chỉnh: Text Encoder, VAE và UNet (chứa Attention Processors)
## Đây chỉ là: file chứa Attn Procs sau khi fine-tune (LoRA)

# ghibli_checkpoint\checkpoint-17000\
attn_lora_path = r"C:\Users\ssm_d\SE2025-14.2\model\ghibli_checkpoint\checkpoint-17000\pytorch_lora_weights.safetensors"
version = "v1"
image_name = "modified_test_6.png"

# ghibli_checkpoint_data_v2\checkpoint-25000\
# attn_lora_path = r"C:\Users\ssm_d\SE2025-14.2\model\ghibli_checkpoint_data_v2\checkpoint-25000\pytorch_lora_weights.safetensors"
# version = "v2"
# image_name = "modified_test_8.png"

# Đường dẫn tới model gốc (ví dụ: pretrained model trên hub)
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")
pipe.unet.load_attn_procs(attn_lora_path)

# Viết prompt
prompt = "Ghibli style a human with wild, red-orange hair and a wide, happy smile looks upward"

# Chạy mô hình
image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]

# Lưu ảnh
image.save(os.path.join(ROOT, "test", "images", version, image_name))
print("Done")