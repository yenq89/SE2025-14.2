# services/quick_nsfw_module.py
import time
from typing import Optional, Tuple

import torch
from PIL import Image
from diffusers import StableDiffusionPipeline


def run_inference(
    pipe: StableDiffusionPipeline,
    prompt: str,
    steps: int = 30,
    cfg_scale: float = 7.5,
    width: int = 512,
    height: int = 512,
    seed: Optional[int] = None,
    negative_prompt: Optional[str] = None,
) -> Tuple[Image.Image, int]:
 
    generator = None
    if seed is not None:
        gen_device = str(getattr(pipe, "device", "cuda" if torch.cuda.is_available() else "cpu"))
        generator = torch.Generator(device=gen_device).manual_seed(seed)

    t0 = time.time()
    out = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=cfg_scale,
        width=width,
        height=height,
        generator=generator,
    )
    inference_ms = int((time.time() - t0) * 1000)

    image = out.images[0]
    return image, inference_ms
