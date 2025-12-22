# ap
from fastapi import APIRouter, HTTPException
from schemas.model import LoadModelReq
from schemas.inference import GenerateReq
from services.sd_service import SDService

router = APIRouter(prefix="/api", tags=["api"])
sd = SDService()

@router.get("/models")
def get_models():
    return {"models": [{"name": n} for n in sd.list_models()]}

@router.get("/model/status")
def get_status():
    return sd.status()

@router.post("/model/load")
def load_model(req: LoadModelReq):
    try:
        return sd.load_model(req.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
def generate(req: GenerateReq):
    try:
        return sd.generate(
            model_name=req.model,
            prompt=req.prompt,
            width=req.width,
            height=req.height,
            steps=req.steps,
            cfg_scale=req.cfgScale,
            seed=req.seed,
            negative_prompt=req.negativePrompt
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
