## Data / Caption generation (Gemini API)

### Tóm tắt
- File notebook `data_processing/Generate_caption_use_GeminiAPI.ipynb` tự động sinh caption cho ảnh dùng Google Gemini (GenAI) và lưu metadata ở dạng JSON Lines.

### Mục đích
- Sinh caption theo phong cách Ghibli để làm `text` cho pipeline fine‑tune (LoRA / Stable Diffusion).

### Prerequisites
- Có API key cho Gemini: đặt biến môi trường `GEMINI_API_KEY` hoặc dùng Secret Manager. **Không** lưu key trực tiếp trong repo.
- Python packages: `google-generativeai`, `Pillow`, `tqdm`, `python-dotenv`, v.v. (notebook đã có cell cài đặt).

### Hoạt động chính (ngắn gọn)
1. Đọc ảnh từ `INPUT_FOLDER` (cấu hình trong notebook).
2. Resize/chuyển sang RGB rồi lưu sang `OUTPUT_FOLDER` với tên số (e.g. `1.jpg`).
3. Gọi API Gemini (model `gemini-2.5-flash`) với prompt định dạng sẵn để sinh caption theo quy tắc (bắt đầu bằng "Ghibli style ...", không nêu tên nhân vật, mô tả giới tính, trang phục, tư thế, bối cảnh).
4. Ghi mỗi entry vào `metadata.jsonl` (một JSON object / dòng) với keys: `file_name`, `text`, `source_file`.
5. Notebook hỗ trợ resume (bỏ qua ảnh đã có trong metadata), handling quota (retry/backoff, stop on ResourceExhausted) và ghi fsync để tránh mất tiến độ.

### Cấu hình quan trọng trong notebook
- `INPUT_FOLDER`, `OUTPUT_FOLDER`, `METADATA_FILE`
- `FORCE_CLEAR_METADATA` (xóa metadata cũ nếu True)
- `RESUME` (bật resume để skip ảnh đã xử lý)
- `AUTO_WAIT_ON_QUOTA`, `QUOTA_WAIT_SECONDS`, `QUOTA_MAX_RETRIES` (xử lý giới hạn quota)

### Lưu ý bảo mật & pháp lý
- Không commit `GEMINI_API_KEY` vào repo; dùng `.env` hoặc Secret Manager.
- Nếu ảnh có hạn chế bản quyền, không public ảnh gốc; chỉ chia sẻ manifest/metadata theo quy định.
