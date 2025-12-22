
from diffusers import StableDiffusionPipeline
import torch
import os

# Đường dẫn lưu ảnh
ROOT = r"C:\Users\ssm_d\SE2025-14.2\webui\image"


# Đường dẫn đến file lora checkpoint đã huấn luyện
attn_lora_path = r"C:\Users\ssm_d\SE2025-14.2\stable-diffusion-webui\models\Stable-diffusion\lora_ghibli_ver3.safetensors"
attn_lora_path = r"C:\Users\ssm_d\SE2025-14.2\stable-diffusion-webui\models\Stable-diffusion\lora_ghibli_ver4.safetensors"
# Hiển thị trên web là tên model được lưu trong thư mục


# Tên ảnh được tạo: Đoạn này anh sửa để gen ảnh theo ngày giờ phút giây giúp em 
image_name = "modified_test_10.png"

# Đường dẫn tới model gốc 
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    safety_checker = None,
    requires_safety_checker = False
)

pipe = pipe.to("cuda")
pipe.unet.load_attn_procs(attn_lora_path)


# Viết prompt
prompt = "Ghibli style, hand drawn, a girl with warm brown hair sits quietly, wearing a simple cream dress and a brown vest"

# Chạy mô hình
image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]

# Lưu ảnh
image.save(os.path.join(ROOT, image_name))
print("Done")