import os
from pathlib import Path
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import router
from core.config import ROOT_IMAGE_DIR

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Stable Diffusion Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Paths ---
BACKEND_DIR = Path(__file__).resolve().parent          # .../software_product/backend
PROJECT_DIR = BACKEND_DIR.parent                      # .../software_product
WEB_DIR = PROJECT_DIR / "web"                         # .../software_product/web

# serve images output
os.makedirs(ROOT_IMAGE_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=ROOT_IMAGE_DIR), name="images")

# API
app.include_router(router)

if WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

@app.get("/health")
def health():
    return {"ok": True}
