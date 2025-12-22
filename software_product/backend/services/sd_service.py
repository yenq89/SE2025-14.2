# services/sd_service
import os
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from services.quick_nsfw_module import run_inference

import torch
from diffusers import StableDiffusionPipeline

from core.config import BASE_MODEL_ID, BASE_MODELS, ROOT_IMAGE_DIR, LORA_DIR, REINIT_PIPE_ON_LOAD

logger = logging.getLogger("sd-webui")

class SDService:
    def __init__(self):
        self._lock = threading.Lock()
        self._pipe: Optional[StableDiffusionPipeline] = None
        self._status: Dict[str, Any] = {
            "status": "not_loaded",   
            "message": "",
            "activeModel": None
        }
        os.makedirs(ROOT_IMAGE_DIR, exist_ok=True)

    def status(self) -> Dict[str, Any]:
        return self._status

    def list_models(self) -> List[str]:
        names: List[str] = []

        names.extend(BASE_MODELS)

        if os.path.isdir(LORA_DIR):
            for fn in os.listdir(LORA_DIR):
                if fn.lower().endswith(".safetensors"):
                    names.append(os.path.splitext(fn)[0])

        return sorted(set(names))


    def _resolve_lora_path(self, model_name: str) -> str:
        for name in self.list_models():
            if name == model_name:
                return os.path.join(LORA_DIR, model_name + ".safetensors")
        raise ValueError(f"Model '{model_name}' not found in {LORA_DIR}")

    def _ensure_pipeline_loaded(self):
        if self._pipe is not None:
            return

        logger.info("Loading base model: %s", BASE_MODEL_ID)
        pipe = StableDiffusionPipeline.from_pretrained(
            BASE_MODEL_ID,
            torch_dtype=torch.float16,
            safety_checker=None,
            requires_safety_checker=False
        )

        device = torch.device("cuda:1") if torch.cuda.is_available() else torch.device("cpu")
        self._pipe = pipe.to(device)
        logger.info("Pipeline ready on device: %s", device)

    @staticmethod
    def _timestamp_filename(prefix: str, ext: str = ".png") -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{ts}{ext}"

    def load_model(self, model_name: str) -> Dict[str, Any]:
        with self._lock:
            self._status.update({"status": "loading", "message": "", "activeModel": None})

            try:
                if model_name in BASE_MODELS:
                    self._pipe = None
                    self._ensure_pipeline_loaded()

                    self._status.update({
                        "status": "loaded",
                        "message": f"Loaded base model: {model_name}",
                        "activeModel": model_name
                    })
                    logger.info("Loaded base model OK: %s", model_name)
                    return self._status

                lora_path = self._resolve_lora_path(model_name)
                logger.info("Requested model=%s, resolved lora_path=%s", model_name, lora_path)

                if REINIT_PIPE_ON_LOAD:
                    self._pipe = None

                self._ensure_pipeline_loaded()

                t0 = time.time()
                self._pipe.unet.load_attn_procs(lora_path)
                dt = int((time.time() - t0) * 1000)

                self._status.update({
                    "status": "loaded",
                    "message": f"Loaded LoRA {model_name} in {dt} ms",
                    "activeModel": model_name
                })
                logger.info("Loaded LoRA OK model=%s in %d ms", model_name, dt)
                return self._status

            except Exception as e:
                logger.exception("Load model failed")
                self._status.update({"status": "failed", "message": str(e), "activeModel": None})
                raise


    def generate(
        self,
        model_name: str,
        prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        if width % 8 != 0 or height % 8 != 0:
            raise ValueError("width/height must be divisible by 8")

        with self._lock:
            if self._status["status"] != "loaded":
                raise ValueError("Model not loaded")

            self._ensure_pipeline_loaded()

            # auto-switch LoRA nếu FE gửi khác activeModel
            if self._status.get("activeModel") != model_name:
                if model_name in BASE_MODELS:
                    logger.info("Switch to base model %s (re-init pipeline)", model_name)
                    self._pipe = None
                    self._ensure_pipeline_loaded()
                    self._status["activeModel"] = model_name
                else:
                    lora_path = self._resolve_lora_path(model_name)
                    logger.info("Auto-switch LoRA to %s (%s)", model_name, lora_path)
                    self._pipe.unet.load_attn_procs(lora_path)
                    self._status["activeModel"] = model_name

            image, inference_ms = run_inference(
                pipe=self._pipe,
                prompt=prompt,
                steps=steps,
                cfg_scale=cfg_scale,
                width=width,
                height=height,
                seed=seed,
                negative_prompt=negative_prompt
            )

            safe_prefix = model_name.replace(" ", "_")
            filename = self._timestamp_filename(safe_prefix, ".png")
            save_path = os.path.join(ROOT_IMAGE_DIR, filename)
            image.save(save_path)

            logger.info("Generated %s in %d ms", save_path, inference_ms)

            return {
                "imageUrl": f"/images/{filename}",
                "inferenceMs": inference_ms,
                "model": model_name
            }
