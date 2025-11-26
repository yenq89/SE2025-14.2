# Pipeline chuẩn bị dữ liệu huấn luyện LoRA phong cách Ghibli

## 📋 Tổng quan

Pipeline tự động xử lý dữ liệu ảnh từ các bộ phim Ghibli để chuẩn bị cho việc huấn luyện mô hình LoRA trên Stable Diffusion 1.5.

**Yêu cầu hệ thống:**
- Python 3.9+ (google-generativeai không hỗ trợ Python 3.8)
- Gemini API Keys (ít nhất 1, khuyến nghị 2-3 keys)

## 🔄 Quy trình 4 bước

### Bước 1: Lọc Ảnh
- **Chức năng**: Loại bỏ ảnh không chứa người
- **Phương pháp**: MediaPipe (nhẹ, nhanh) hoặc YOLOv8 (chính xác hơn)
- **Output**: Ảnh đã lọc lưu vào thư mục tạm

### Bước 2: Resize ảnh
- **Kích thước**: 512x512 pixels
- **Phương pháp**: LANCZOS resize (square frame → 512×512)
- **Input**: Ảnh đã lọc từ Bước 1 (square frame, tỷ lệ 1:1)
- **Output**: Ảnh resize lưu vào `data/ghibli/train/`

**Tại sao sử dụng LANCZOS resampling?**

**Bối cảnh ảnh gốc:**
- Ảnh được capture từ phim với **Auto Screen Capture tool**
- Frame size gốc: **Square frame** (tỷ lệ 1:1 - ví dụ: 997×997, 1257×1257)
- Nguồn: Video 1080p (1920×1080) → tool tự động crop square từ giữa màn hình
- **Vì đã là square (1:1), chỉ cần resize trực tiếp về 512×512**

✅ **Ưu điểm của LANCZOS Resampling:**

1. **Chất lượng cao nhất:**
   - Thuật toán resize chất lượng cao nhất trong Pillow
   - Giữ chi tiết sắc nét hơn OpenCV INTER_LINEAR/INTER_CUBIC
   - Ít bị artifacts (răng cưa, blur) khi scale down từ 997→512
   - Phù hợp cho ảnh anime/illustration (đường nét rõ ràng)

2. **Phù hợp với Ghibli style:**
   - Giữ nguyên độ sắc nét của đường vẽ tay
   - Bảo toàn chi tiết biểu cảm khuôn mặt
   - Không làm mờ texture (tóc, quần áo, background)
   - Tối ưu cho training LoRA (model học đúng phong cách)

**So sánh với các phương pháp khác:**
```python
# ❌ OpenCV INTER_LINEAR - nhanh nhưng kém chất lượng
img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
# → Ảnh bị mờ, mất chi tiết đường nét

# ⚠️ OpenCV INTER_CUBIC - tốt hơn LINEAR nhưng vẫn kém LANCZOS
img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_CUBIC)
# → Chất lượng khá nhưng vẫn có artifacts nhẹ

# ✅ Pillow LANCZOS - chất lượng cao nhất (dataset hiện tại)
img = Image.open(image_path)  # Square frame 
img = img.resize((512, 512), Image.Resampling.LANCZOS)
# → Chi tiết sắc nét, không bị blur, phù hợp anime/illustration
```

**Kết quả:**
- Ảnh giữ nguyên tỷ lệ 1:1 (square frame → 512×512)
- Chi tiết sắc nét, không bị blur hay artifacts
- Đường nét vẽ tay được bảo toàn
- Phù hợp cho training LoRA Stable Diffusion 1.5

### Bước 3: Tạo caption với Model Failover Strategy (chi tiết tại file `FAILOVER_STRATEGY.md`)
- **API**: Google Gemini với 4 models/key
- **Model Priority** (mỗi API key):
  1. `gemini-2.5-flash` - Chất lượng cao, tốc độ tốt
  2. `gemini-2.5-flash-lite` 
  3. `gemini-2.0-flash` 
  4. `gemini-2.0-flash-lite` 

- **Xử lý lỗi thông minh**:
  - ✅ **Rate Limit (429)** → Exponential Backoff (5s → 10s → 20s → 40s → 80s)
  - ✅ **Quota Exceeded (RPD/TPD)** → Chuyển model tiếp theo ngay lập tức
  - ✅ **Hết models trong key** → Chuyển sang API key tiếp theo, reset về model đầu
  - ✅ **Checkpoint/Resume** → Lưu trạng thái (key + model + ảnh đã xử lý)
  - ✅ **Progress tracking** → Hiển thị tiến độ realtime

### Bước 4: Lưu Output
- **Thư mục**: `data/ghibli/train/`
- **Files**:
  - Ảnh: `1.jpg`, `2.jpg`, ... (512x512)
  - Caption: `metadata.jsonl` (format: `{"file_name": "1.jpg", "text": "Ghibli style..."}`)

## 🚀 Cài đặt & Sử dụng

### 1. Kiểm tra Python version

```powershell
python --version
# Phải là Python 3.9 trở lên
# Nếu đang dùng Python 3.8 → Nâng cấp lên Python 3.11+
```

### 2. Cài đặt dependencies

```powershell
pip install -r data_processing/scripts/requirements.txt
```

**Lưu ý:**
- Nếu không cần lọc ảnh (đã có ảnh sạch), có thể bỏ qua `mediapipe` và `opencv-python`
- Chỉ cần cài 1 trong 2: MediaPipe (nhẹ) hoặc YOLOv8 (chính xác)

### 3. Cấu hình API Keys

**Bước 3.1:** Tạo file `.env` từ template:

```powershell
Copy-Item data_processing/scripts/.env.example data_processing/scripts/.env
```

**Bước 3.2:** Lấy API keys từ Google AI Studio:
- Truy cập: https://aistudio.google.com/apikey
- Tạo API keys (khuyến nghị 2-3 keys)
- Copy keys

**Bước 3.3:** Chỉnh sửa `.env` và thêm API keys:

```env
GEMINI_API_KEY_1=your_api_key_here
GEMINI_API_KEY_2=your_api_key_here
GEMINI_API_KEY_3=your_api_key_here
```

**Lưu ý quan trọng:**
- Có thể dùng 1 key, nhưng nên có 2-3 keys để tránh gián đoạn
- Pipeline tự động chuyển key khi hết quota

### 4. Test API Keys (Khuyến nghị)

Trước khi chạy pipeline, test xem API keys có hoạt động không:

```powershell
cd data_processing/scripts/
python test_gemini_api.py
```

Output mong đợi:
```
✅ Key #1 HOẠT ĐỘNG!
✅ Key #2 HOẠT ĐỘNG!
```

### 5. Chạy Pipeline

#### **Chạy đầy đủ (từ đầu):**

```powershell
python pipeline_build_caption.py
```

Pipeline sẽ tự động:
1. Lọc ảnh có người
2. Đổi tên theo số (1.jpg, 2.jpg, ...)
3. Resize về 512x512
4. Gen caption với Gemini
5. Lưu vào `data/ghibli/train/`

#### **Chỉ chạy gen caption (nếu đã có ảnh resize):**

Sửa dòng cuối trong `pipeline_build_caption.py`:
```python
pipeline.run(skip_filter=True, skip_resize=True)
```

Sau đó chạy:
```powershell
python pipeline_build_caption.py
```

#### **Bỏ qua lọc ảnh (dùng tất cả ảnh):**

```python
pipeline.run(skip_filter=True, skip_resize=False)
```

### 6. Resume khi bị dừng

Pipeline tự động lưu checkpoint. Nếu bị dừng giữa chừng (hết quota, mất mạng,...), chỉ cần chạy lại:

```powershell
python pipeline_build_caption.py
```

Pipeline sẽ:
- ✅ Đọc checkpoint
- ✅ Khôi phục đúng API key + model đang dùng
- ✅ Tiếp tục từ ảnh tiếp theo (không lặp lại)

## 📊 Ước tính Quota & Capacity

### **Free Tier (Một API Key)**

| Model | RPM | RPD | TPM | Ưu điểm |
|-------|-----|-----|-----|---------|
| **gemini-2.5-flash** | 10 | 250 | 250K | Chất lượng tốt, cân bằng |
| **gemini-2.5-flash-lite** | 15 | 1000 | 250K | RPM cao hơn (nhanh) |
| **gemini-2.0-flash** | 15 | 200 | 1M | TPM cao (xử lý ảnh lớn) |
| **gemini-2.0-flash-lite** | 30 | 200 | 1M | RPM cao nhất |

**Giải thích:**
- **RPM** (Requests Per Minute): Số request/phút
- **RPD** (Requests Per Day): Số request/ngày
- **TPM** (Tokens Per Minute): Số tokens/phút

### **Capacity tổng với 3 API Keys**

```
Mỗi key × 4 models = Nhiều cơ hội xử lý

Key 1:
  ├─ gemini-2.5-flash → ~240 ảnh (quota RPD)
  ├─ gemini-2.5-flash-lite → ~990 ảnh
  ├─ gemini-2.0-flash → ~190 ảnh
  └─ gemini-2.0-flash-lite → ~190 ảnh

Key 2: (Tương tự)
Key 3: (Tương tự)

Thực tế: ~4,500 ảnh/ngày (do quota có thể shared giữa models)
```

## 🛠 Xử lý lỗi & Troubleshooting

### **Lỗi 1: Rate Limit (429)**

**Triệu chứng:**
```
⏳ Rate Limit! Chờ 10.0s trước khi thử lại... (lần 2/5)
```

**Nguyên nhân:** Request quá nhanh (vượt RPM)

**Cách xử lý tự động:**
- Pipeline tự động áp dụng Exponential Backoff
- Chờ: 5s → 10s → 20s → 40s → 80s
- Nếu vẫn lỗi sau 5 lần → Chuyển sang model tiếp theo

**Không cần làm gì!** Pipeline tự xử lý.

---

### **Lỗi 2: Hết Quota (Resource Exhausted)**

**Triệu chứng:**
```
⚠ Model hiện tại đã hết quota (RPD/TPD)
⟳ Chuyển sang model: gemini-2.5-flash-lite (ưu tiên #2)
```

**Nguyên nhân:** Đã dùng hết RPD của model

**Cách xử lý tự động:**
- Chuyển ngay sang model tiếp theo trong cùng key
- Nếu hết 4 models → Chuyển sang API key tiếp theo
- Reset về model đầu tiên

**Nếu hết tất cả keys:**
```
✗ Đã hết tất cả API keys và models!
```
→ **Giải pháp:**
1. Chờ 24h để quota reset
2. Thêm API key mới vào `.env`
3. Chạy lại pipeline (sẽ resume từ checkpoint)

---

### **Lỗi 3: API Key không hợp lệ**

**Triệu chứng:**
```
ValueError: Không tìm thấy API key nào!
```
hoặc
```
403 API key not valid
```

**Giải pháp:**
1. Kiểm tra file `.env` có tồn tại không
2. Kiểm tra API key có đúng format không (bắt đầu bằng `AIza.....`)
3. Test API key:
   ```powershell
   python test_gemini_api.py
   ```

---

### **Lỗi 4: Không phát hiện được người (MediaPipe/YOLO)**

**Triệu chứng:**
```
⚠ Không tìm thấy thư viện phát hiện người. Bỏ qua bước lọc.
```

**Giải pháp:**

**Option 1 - MediaPipe (nhẹ, khuyến nghị):**
```powershell
pip install mediapipe opencv-python
```

**Option 2 - YOLOv8 (chính xác hơn):**
```powershell
pip install ultralytics
```

**Option 3 - Bỏ qua lọc:**
```python
# Dùng tất cả ảnh, không lọc
pipeline.run(skip_filter=True)
```

---

### **Lỗi 5: Python 3.8 không tương thích**

**Triệu chứng:**
```
ERROR: No matching distribution found for google-generativeai>=0.8.0
```

**Giải pháp:** Nâng cấp Python lên 3.9+
1. Tải Python 3.11+: https://www.python.org/downloads/
2. Cài đặt (check "Add to PATH")
3. Chạy lại:
   ```powershell
   pip install -r data_processing/scripts/requirements.txt
   ```


---

### **Monitoring Logs**

Pipeline hiển thị log chi tiết:

```
✓ Sử dụng API Key #1/3 | Model: gemini-2.5-flash (1/4)
  Tạo caption: 15%|███░░░░░░░| 150/1000

⏳ Rate Limit! Chờ 5.0s...
✓ Thành công

  Tạo caption: 100%|██████████| 1000/1000
⚠ Model hiện tại đã hết quota (RPD/TPD)
⟳ Chuyển sang model: gemini-2.5-flash-lite (ưu tiên #2)

✓ Sử dụng API Key #1/3 | Model: gemini-2.5-flash-lite (2/4)
  Tạo caption: 30%|█████░░░░░| 300/1000
```

**Ý nghĩa:**
- Hiển thị key & model đang dùng
- Progress bar realtime
- Tự động chuyển đổi khi cần
- Lưu checkpoint sau mỗi ảnh

**Lưu ý:**
- Thư mục `filtered_temp` sẽ tự động tạo và có thể xóa sau khi resize xong
- Thư mục `train` chứa dữ liệu cuối cùng để huấn luyện LoRA

### **Kiểm tra nếu gặp vấn đề:**

1. **File `.env` có tồn tại không?**
   ```powershell
   Test-Path .env
   # True = OK, False = Chưa tạo
   ```

2. **API keys có đúng format không?**
   ```powershell
   python test_gemini_api.py
   ```

3. **Python version có đúng không?**
   ```powershell
   python --version
   # Phải >= 3.9
   ```

4. **Dependencies đã cài đủ chưa?**
   ```powershell
   pip list | Select-String "generativeai|Pillow|tqdm"
   ```

5. **Thư mục input có ảnh không?**
   ```powershell
   Get-ChildItem ghibli_data -Recurse -Filter *.jpg | Measure-Object
   ```

### **Links hữu ích:**
- Google AI Studio: https://aistudio.google.com/
- Gemini API Docs: https://ai.google.dev/docs
- Python Download: https://www.python.org/downloads/

### **Best Practices:**

1. ✅ **Luôn test API keys trước** với `test_gemini_api.py`
2. ✅ **Cấu hình ít nhất 2 API keys** để tránh gián đoạn
3. ✅ **Backup checkpoint.json** định kỳ khi chạy lâu
4. ✅ **Monitor logs** để điều chỉnh kịp thời
5. ✅ **Chạy thử với 10-20 ảnh** trước khi xử lý hàng nghìn ảnh
6. ✅ **Kiểm tra quota còn lại** tại AI Studio trước khi chạy batch lớn

---

**Pipeline này đảm bảo chạy ổn định, tự động xử lý lỗi và tối ưu hóa việc sử dụng Gemini API Free Tier!** 🚀
