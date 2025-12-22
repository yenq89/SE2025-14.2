export const $ = (id) => document.getElementById(id);

export function setDebug(obj) {
  $("debug").textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
}

export function showError(msg) {
  const box = $("err");
  if (!msg) { box.style.display = "none"; box.textContent = ""; return; }
  box.style.display = "block";
  box.textContent = msg;
}

export function setOverlay(on, text = "Running...") {
  $("overlayText").textContent = text;
  $("overlay").classList.toggle("on", !!on);
}

export function setStatus(status, message = "") {
  const dot = $("dot");
  dot.className = "dot";

  let top = "UNKNOWN";
  let sub = message || "—";

  if (status === "loaded") { dot.classList.add("ok"); top = "LOADED"; }
  else if (status === "failed") { dot.classList.add("bad"); top = "FAILED"; }
  else if (status === "loading") { dot.classList.add("run"); top = "LOADING"; }
  else if (status === "running") { dot.classList.add("run"); top = "RUNNING"; }
  else { top = "NOT_LOADED"; sub = "Model chưa load"; }

  $("statusTop").textContent = top;
  $("statusText").textContent = sub;

  const canGen = (status === "loaded");
  $("btnGen").disabled = !canGen;
  $("hintLine").textContent = canGen ? "Model đã load → có thể Generate." : "Model chưa load → không cho generate.";
}

export function clearImage() {
  $("img").style.display = "none";
  $("ph").style.display = "flex";
  $("openFull").style.display = "none";
  $("download").style.display = "none";
  $("timeInfo").textContent = "—";
  $("metaTitle").textContent = "Inference";
  $("img").src = "";
}

export function showImageByUrl(apiBase, imageUrl, inferenceMs, modelName) {
  const origin = apiBase || window.location.origin;
  const full = new URL(imageUrl, origin).toString();

  $("img").src = full;
  $("img").style.display = "block";
  $("ph").style.display = "none";

  $("openFull").href = full;
  $("download").href = full;
  $("openFull").style.display = "inline-flex";
  $("download").style.display = "inline-flex";

  $("metaTitle").textContent = modelName ? `Inference — ${modelName}` : "Inference";
  $("timeInfo").textContent = (inferenceMs != null) ? `${inferenceMs} ms` : "—";
}

export function bindRange(id, outId, fmt = (v) => v) {
  const el = $(id), out = $(outId);
  const update = () => out.textContent = fmt(el.value);
  el.addEventListener("input", update);
  update();
}
