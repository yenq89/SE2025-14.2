import { createApiClient } from "./api.js";
import { $, setDebug, showError, setOverlay, setStatus, clearImage, showImageByUrl, bindRange } from "./ui.js";

const API_BASE = "http://127.0.0.1:8000";

$("apiBaseLabel").textContent = API_BASE || "(same origin)";
const api = createApiClient(API_BASE);

function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

async function loadModelList() {
  showError("");
  setDebug({ action: "GET /api/models" });
  const data = await api.listModels();
  setDebug({ action: "GET /api/models", response: data });

  const sel = $("modelSelect");
  sel.innerHTML = "";

  const models = data.models || [];
  models.sort((a, b) => {
  if (a.name === "SD_ver1.5") return -1;
  if (b.name === "SD_ver1.5") return 1;
  return a.name.localeCompare(b.name);
});
  if (models.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "(Không tìm thấy .safetensors trong LORA_DIR)";
    sel.appendChild(opt);
    return;
  }

  for (const m of models) {
    const opt = document.createElement("option");
    opt.value = m.name;
    opt.textContent = m.name;
    sel.appendChild(opt);
  }
}

async function checkStatus() {
  showError("");
  setDebug({ action: "GET /api/model/status" });
  const data = await api.status();
  setDebug({ action: "GET /api/model/status", response: data });

  const s = (data.status || "unknown").toLowerCase();
  if (s === "loaded") setStatus("loaded", data.activeModel || "ready");
  else if (s === "loading") setStatus("loading", data.message || "");
  else if (s === "failed") setStatus("failed", data.message || "");
  else setStatus("not_loaded", "");
}

async function loadModel() {
  showError("");
  clearImage();

  const model = $("modelSelect").value;
  if (!model) return showError("Chưa chọn model.");

  setStatus("loading", "Loading model...");
  setOverlay(true, "Loading model...");
  setDebug({ action: "POST /api/model/load", request: { model } });

  try {
    const data = await api.loadModel(model);
    setDebug({ action: "POST /api/model/load", response: data });

    const st = (data.status || "").toLowerCase();
    if (st === "loaded") setStatus("loaded", data.activeModel || model);
    else if (st === "failed") setStatus("failed", data.message || "failed");
    else setStatus(st || "loading", data.message || "");
  } finally {
    setOverlay(false);
  }
}

async function generate() {
  showError("");
  clearImage();

  const model = $("modelSelect").value;
  const prompt = $("prompt").value.trim();
  if (!model) return showError("Chưa chọn model.");
  if (!prompt) return showError("Prompt rỗng.");

  const width = parseInt($("width").value || "512", 10);
  const height = parseInt($("height").value || "512", 10);
  const steps = parseInt($("steps").value || "30", 10);
  const cfgScale = parseFloat($("cfgScale").value || "7.5");
  const seedStr = $("seed").value.trim();
  const seed = seedStr ? parseInt(seedStr, 10) : null;
  const negativePrompt = $("neg").value.trim() || null;

  if (width % 8 !== 0 || height % 8 !== 0) {
    return showError("width/height phải chia hết cho 8 (vd 512, 640, 768...).");
  }

  setStatus("running", "Inference...");
  setOverlay(true, "Running inference...");
  $("btnGen").disabled = true;

  const req = {
    model,
    prompt,
    width: clamp(width, 256, 768),
    height: clamp(height, 256, 768),
    steps: clamp(steps, 10, 50),
    cfgScale: clamp(cfgScale, 1, 12),
    seed,
    negativePrompt,
  };

  setDebug({ action: "POST /api/generate", request: req });

  try {
    const data = await api.generate(req);
    setDebug({ action: "POST /api/generate", response: data });

    showImageByUrl(API_BASE, data.imageUrl, data.inferenceMs, data.model || model);
    setStatus("loaded", data.model || model);
  } finally {
    setOverlay(false);
    $("btnGen").disabled = false;
  }
}

/* sliders -> value text */
bindRange("width", "wVal", (v) => v);
bindRange("height", "hVal", (v) => v);
bindRange("steps", "sVal", (v) => v);
bindRange("cfgScale", "cVal", (v) => Number(v).toFixed(1));

/* Ctrl/⌘ + Enter */
$("prompt").addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    if (!$("btnGen").disabled) {
      generate().catch(err => {
        showError(String(err.message || err));
        setStatus("loaded", "ready");
        setOverlay(false);
      });
    }
  }
});

/* wiring */
$("btnLoad").addEventListener("click", () =>
  loadModel().catch(e => { showError(String(e.message || e)); setStatus("failed", "load error"); setOverlay(false); })
);
$("btnStatus").addEventListener("click", () =>
  checkStatus().catch(e => showError(String(e.message || e)))
);
$("btnGen").addEventListener("click", () =>
  generate().catch(e => { showError(String(e.message || e)); setStatus("loaded", "ready"); setOverlay(false); })
);

$("chipApi").addEventListener("click", async () => {
  const val = API_BASE || window.location.origin;
  try {
    await navigator.clipboard.writeText(val);
    $("statusText").textContent = `Copied API base: ${val}`;
    setTimeout(() => checkStatus().catch(() => {}), 800);
  } catch {}
});

/* init */
clearImage();
setStatus("not_loaded", "");
loadModelList()
  .then(checkStatus)
  .catch(e => showError(String(e.message || e)));
