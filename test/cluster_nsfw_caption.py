# cluster_nsfw_caption.py đọc kết quả từ metadata.jsonl,
# thực hiện tokenize, phân cụm vector đầu ra của tokenizer để phân tích sâu hơn về
# các lý do tạo NSFW. Tuy nhiên, quá trình này đang bị dừng.

# cluster_nsfw_captions.py
import os, json
from pathlib import Path
from tqdm import tqdm
import torch
import numpy as np

from diffusers import StableDiffusionPipeline
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
# import umap               # optional: pip install umap-learn
# import matplotlib.pyplot as plt

# ====== CONFIG ======
NSFW_METADATA = r"C:\Users\ssm_d\SE2025-14.2\test\nsfw_data\metadata.jsonl"
OUT_JSONL = r"C:\Users\ssm_d\SE2025-14.2\test\nsfw_data\nsfw_clusters.jsonl"
DEVICE = "cuda"
BATCH = 16
MAX_TOKENS = 77
# ====================

# ---- load pipeline (only for tokenizer + text_encoder) ----
print("Loading pipeline (text encoder + tokenizer)...")
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
pipe = pipe.to(DEVICE)

tokenizer = pipe.tokenizer
text_encoder = pipe.text_encoder   # usually a CLIPTextModel

# helper: tokenize and get pooled embedding
def get_text_embedding(texts, max_length=MAX_TOKENS, device=DEVICE):
    # texts: list[str]
    inputs = tokenizer(texts, padding="max_length", truncation=True, max_length=max_length, return_tensors="pt")
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
    with torch.no_grad():
        outputs = text_encoder(input_ids=input_ids, attention_mask=attention_mask)
        # CLIP TextModel usually returns last_hidden_state: (B, T, D)
        last_hidden = outputs.last_hidden_state  # (B, T, D)
        # pooling: take mean over tokens with attention_mask
        mask = attention_mask.unsqueeze(-1)
        summed = (last_hidden * mask).sum(1)
        counts = mask.sum(1).clamp(min=1)
        pooled = summed / counts  # (B, D)
        # normalize
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
        return pooled.cpu().numpy()  # as numpy array

# ---- read captions ----
items = []
with open(NSFW_METADATA, "r", encoding="utf-8") as f:
    for line in f:
        try:
            obj = json.loads(line)
            items.append(obj)
        except:
            pass

texts = [it.get("text","") for it in items]
names = [it.get("file_name","") for it in items]

print("Loaded", len(texts), "captions")

# ---- compute embeddings in batches ----
embs = []
for i in range(0, len(texts), BATCH):
    batch = texts[i:i+BATCH]
    emb = get_text_embedding(batch)
    embs.append(emb)
embs = np.vstack(embs)
print("Embeddings shape:", embs.shape)

# # ---- optional: reduce dim for speed/visualization ----
# pca = PCA(n_components=64, random_state=0)
# emb_low = pca.fit_transform(embs)  # (N,64)

# ---- clustering: KMeans (k selection by silhouette) ----
best_k = 0
best_sil = -1
best_labels = None
for k in range(2, min(6, len(texts))):
    km = KMeans(n_clusters=k, random_state=0).fit(embs)
    labels = km.labels_
    sil = silhouette_score(embs, labels) if len(set(labels))>1 else -1
    if sil > best_sil:
        best_sil = sil
        best_k = k
        best_labels = labels
print("Best K:", best_k, "silhouette:", best_sil)

# fallback if clustering failed
if best_labels is None:
    km = KMeans(n_clusters=2, random_state=0).fit(embs)
    best_labels = km.labels_

# # ---- alternative: DBSCAN for noise detection ----
# db = DBSCAN(eps=0.5, min_samples=3).fit(emb_low)
# db_labels = db.labels_  # -1 = noise

# ---- choose which labels to keep (you can choose km or db) ----
labels_use = best_labels  # or db_labels

# ---- save output mapping ----
with open(OUT_JSONL, "w", encoding="utf-8") as fo:
    for it, name, text, lab in zip(items, names, texts, labels_use):
        out = {"file_name": name, "text": text, "cluster": int(lab)}
        fo.write(json.dumps(out, ensure_ascii=False) + "\n")

print("Saved clusters to", OUT_JSONL)

# ---- quick inspection: print top 5 captions per cluster ----
from collections import defaultdict
byc = defaultdict(list)
for name, text, lab in zip(names, texts, labels_use):
    byc[lab].append(text)

for lab, lst in byc.items():
    print(f"\nCluster {lab} (size {len(lst)}):")
    for s in lst[:5]:
        print("-", s)

# # ---- visualization (UMAP 2D) optional ----
# try:
#     reducer = umap.UMAP(n_components=2, random_state=0)
#     emb_2d = reducer.fit_transform(emb_low)
#     plt.figure(figsize=(8,6))
#     sc = plt.scatter(emb_2d[:,0], emb_2d[:,1], c=labels_use, cmap="tab10", s=8)
#     plt.colorbar(sc)
#     plt.title("NSFW captions clusters (2D UMAP)")
#     plt.savefig(os.path.join(Path(NSFW_METADATA).parent, "clusters_umap.png"), dpi=200)
#     print("Saved UMAP plot")
# except Exception as e:
#     print("UMAP/plot skipped:", e)