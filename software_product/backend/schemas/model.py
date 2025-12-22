# schemas/model.py
from pydantic import BaseModel, Field

class LoadModelReq(BaseModel):
    model: str = Field(..., min_length=1, max_length=200)

class ModelItem(BaseModel):
    name: str

class ModelListRes(BaseModel):
    models: list[ModelItem]
