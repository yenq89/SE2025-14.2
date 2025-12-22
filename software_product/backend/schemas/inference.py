# schemas/inference.py
from pydantic import BaseModel, Field
from typing import Optional

class GenerateReq(BaseModel):
    model: str = Field(..., min_length=1, max_length=200)
    prompt: str = Field(..., min_length=1, max_length=500)

    width: int = Field(512, ge=256, le=768)
    height: int = Field(512, ge=256, le=768)
    steps: int = Field(30, ge=10, le=50)
    cfgScale: float = Field(7.5, ge=1.0, le=12.0)

    seed: Optional[int] = None
    negativePrompt: Optional[str] = None

class GenerateRes(BaseModel):
    imageUrl: str
    inferenceMs: int
    model: str
