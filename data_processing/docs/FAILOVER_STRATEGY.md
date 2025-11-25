# Model Failover Strategy - Chiến Lược Chuyển Đổi Mô Hình

## 📊 Tổng Quan

Pipeline sử dụng **Model Failover Strategy** để đảm bảo hoạt động liên tục, tối ưu hóa việc sử dụng quota và xử lý các giới hạn API một cách thông minh.

## 🎯 Nguyên Tắc Hoạt Động

### 1. **Thứ Tự Ưu Tiên Models (Mỗi API Key)**

| Ưu Tiên | Model | Đặc Điểm | Khi Nào Chuyển |
|---------|-------|----------|----------------|
| **A.1** | `gemini-2.5-flash` | Chất lượng cao, tốc độ tốt | RPD/RPM exceeded → A.2 |
| **A.2** | `gemini-2.5-flash-lite` | RPD cao hơn | RPD/RPM exceeded → A.3 |
| **A.3** | `gemini-2.0-flash` | TPM cao hơn | RPD/RPM exceeded → A.4 |
| **A.4** | `gemini-2.0-flash-lite` | RPM cao nhất | RPD/RPM exceeded → Key tiếp |

### 2. **Cascade Flow - Luồng Chuyển Đổi**

```
Key 1 + Model A.1
    ↓ (Rate Limit)
    Exponential Backoff (5s → 10s → 20s → 40s → 80s)
    ↓ (Vẫn thất bại)
    Key 1 + Model A.2
    ↓ (Quota Exceeded)
    Key 1 + Model A.3
    ↓ (Quota Exceeded)
    Key 1 + Model A.4
    ↓ (Quota Exceeded)
    Key 2 + Model A.1 (Reset về model đầu)
    ↓
    ... (Tương tự)
    ↓
    Key 3 + Models
    ↓
    Hết tất cả → Dừng pipeline
```

## 🔧 Xử Lý Lỗi Chi Tiết

### **Lỗi 1: Rate Limit (429 - RPM/TPM)**

**Triệu chứng:**
- `429 Too Many Requests`
- `RATE_LIMIT_EXCEEDED`
- Requests per minute (RPM) quá cao

**Giải pháp: Exponential Backoff**

```python
Lần 1: Chờ 5 giây
Lần 2: Chờ 10 giây
Lần 3: Chờ 20 giây
Lần 4: Chờ 40 giây
Lần 5: Chờ 80 giây (tối đa)
```

**Nếu vẫn thất bại sau 5 lần:**
→ Chuyển sang model tiếp theo trong cùng API key

**Lý do:** Rate limit là tạm thời, chờ một chút sẽ hết. Không cần đổi model ngay.

---

### **Lỗi 2: Quota Exceeded (RPD/TPD)**

**Triệu chứng:**
- `RESOURCE_EXHAUSTED`
- `Quota exceeded for quota metric`
- Requests per day (RPD) đã hết

**Giải pháp: Chuyển Model Ngay Lập Tức**

```
Key 1 + gemini-2.5-flash (hết quota)
    ↓ (Không chờ, chuyển ngay)
Key 1 + gemini-2.5-flash-lite (RPD độc lập)
    ↓ (Nếu hết)
Key 1 + gemini-2.0-flash
    ↓ (Nếu hết)
Key 1 + gemini-2.0-flash-lite
    ↓ (Nếu hết tất cả models)
Key 2 + gemini-2.5-flash (Key mới, quota mới)
```

**Lý do:** Mỗi model có quota riêng. Chuyển model = tận dụng quota mới.

---

### **Lỗi 3: Các Lỗi Khác**

**Triệu chứng:**
- Network errors
- Server errors (500, 503)
- Invalid response

**Giải pháp: Retry với delay ngắn**

```python
Retry 5 lần, mỗi lần chờ 2 giây
Nếu vẫn lỗi → Báo lỗi và bỏ qua ảnh đó
```

## 📈 Ước Tính Capacity

### **Free Tier (Một API Key)**

| Model | RPM | RPD | TPM | Ưu điểm |
|-------|-----|-----|-----|---------||
| **gemini-2.5-flash** | 10 | 250 | 250K | Chất lượng tốt, cân bằng |
| **gemini-2.5-flash-lite** | 15 | 1000 | 250K | RPM cao hơn (nhanh) |
| **gemini-2.0-flash** | 15 | 200 | 1M | TPM cao (xử lý ảnh lớn) |
| **gemini-2.0-flash-lite** | 30 | 200 | 1M | RPM cao nhất |

**Giải thích:**
- **RPM** (Requests Per Minute): Số request/phút
- **RPD** (Requests Per Day): Số request/ngày
- **TPM** (Tokens Per Minute): Số tokens/phút

### **Capacity Tổng Với Nhiều Keys**

```
Mỗi Key:
  ├─ gemini-2.5-flash → 250 ảnh/ngày
  ├─ gemini-2.5-flash-lite → 1,000 ảnh/ngày
  ├─ gemini-2.0-flash → 200 ảnh/ngày
  └─ gemini-2.0-flash-lite → 200 ảnh/ngày

Một Key: ~1,650 ảnh/ngày (tổng 4 models)
Ba Keys: ~4,950 ảnh/ngày
Năm Keys: ~8,250 ảnh/ngày
```

**Lưu ý:** Các model khác nhau có quota riêng biệt, có thể tận dụng song song.

## 🎮 Ví Dụ Thực Tế

### **Scenario 1: Pipeline Chạy Mượt**

```
1. Bắt đầu với Key 1 + gemini-2.5-flash
2. Gen 100 ảnh → OK
3. Gặp rate limit → Chờ 2s → OK
4. Gen tiếp 200 ảnh → OK
5. Hết quota gemini-2.5-flash (1,500 ảnh)
6. Tự động chuyển → Key 1 + gemini-2.5-flash-lite
7. Gen tiếp 300 ảnh → OK
...
```

### **Scenario 2: Xử Lý Rate Limit**

```
1. Key 1 + gemini-2.5-flash
2. Gen quá nhanh → Rate Limit (429)
3. Exponential Backoff:
   - Lần 1: Chờ 5s → Thử lại → Vẫn lỗi
   - Lần 2: Chờ 10s → Thử lại → Vẫn lỗi
   - Lần 3: Chờ 20s → Thử lại → OK!
4. Tiếp tục gen caption...
```

### **Scenario 3: Hết Quota RPD**

```
1. Key 1 + gemini-2.5-flash gen 250 ảnh
2. Hết quota RPD → RESOURCE_EXHAUSTED
3. Tự động chuyển → Key 1 + gemini-2.5-flash-lite (quota mới)
4. Gen tiếp 1,000 ảnh → Hết quota
5. Chuyển → Key 1 + gemini-2.0-flash
6. Gen tiếp 200 ảnh → Hết quota
7. Chuyển → Key 1 + gemini-2.0-flash-lite
8. Gen tiếp 200 ảnh → Hết quota (hết tất cả models của Key 1)
9. Chuyển → Key 2 + gemini-2.5-flash (reset về model đầu)
10. Tiếp tục với Key 2 (250 + 1,000 + 200 + 200 = ~1,650 ảnh nữa)...
```

## 🛡️ Checkpoint & Resume

### **Checkpoint lưu gì?**

```json
{
  "last_processed": 1234,
  "total_images": 5000,
  "current_key_index": 1,
  "current_model_index": 2,
  "current_model": "gemini-2.0-flash",
  "timestamp": "2025-11-18 14:30:45"
}
```

### **Khi Resume:**

```python
1. Đọc checkpoint
2. Khôi phục:
   - Key #2
   - Model: gemini-2.0-flash
   - Ảnh #1235 (tiếp theo sau 1234)
3. Tiếp tục gen caption từ đúng vị trí
```

**Lợi ích:**
- ✅ Không mất công gen lại
- ✅ Không lộn xộn thứ tự
- ✅ Tiếp tục đúng model & key đã dùng

## 🔍 Monitoring & Debugging

### **Log Output Ví Dụ:**

```
✓ Sử dụng API Key #1/3 | Model: gemini-2.5-flash (1/4)
  Tạo caption: 100%|██████████| 250/5000

⏳ Rate Limit! Chờ 10.0s trước khi thử lại... (lần 2/5)
✓ Thành công sau retry

⚠ Model hiện tại đã hết quota (RPD/TPD)
⟳ Chuyển sang model: gemini-2.5-flash-lite (ưu tiên #2)
✓ Sử dụng API Key #1/3 | Model: gemini-2.5-flash-lite (2/4)
  Tạo caption: 120%|██████████| 600/5000

⚠ Model hiện tại đã hết quota (RPD/TPD)
⟳ Chuyển sang model: gemini-2.0-flash (ưu tiên #3)
✓ Sử dụng API Key #1/3 | Model: gemini-2.0-flash (3/4)

...

⚠ Model hiện tại đã hết quota (RPD/TPD)
⟳ Chuyển sang API Key #2/3
✓ Sử dụng API Key #2/3 | Model: gemini-2.5-flash (1/4)
  Tạo caption: 180%|██████████| 900/5000
```

## ⚙️ Tùy Chỉnh Strategy

### **Thay Đổi Thứ Tự Models:**

```python
# Trong Config class
MODEL_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",        # Bỏ qua lite models
]
```

### **Điều Chỉnh Backoff:**

```python
# Trong Config class
INITIAL_BACKOFF = 5   # Mặc định: 5s (có thể tăng nếu rate limit liên tục)
MAX_BACKOFF = 64      # Mặc định: 64s (có thể tăng lên 120s)
MAX_RETRIES_RATE_LIMIT = 5  # Mặc định: 5 lần (có thể tăng lên 10)
```

### **Chỉ Dùng 1 Model:**

```python
MODEL_PRIORITY = [
    "gemini-2.5-flash",  # Chỉ dùng flash, ổn định
]
```

## 📊 So Sánh Strategies

| Strategy | Ưu Điểm | Nhược Điểm | Phù Hợp Khi |
|----------|---------|-----------|-------------|
| **Single Model + Multi Keys** | Đơn giản | Không tận dụng hết quota | Dùng model Pro |
| **Multi Models + Single Key** | Tối ưu quota | Giới hạn bởi 1 key | Có ít keys |
| **Multi Models + Multi Keys** ⭐ | Tối ưu toàn diện | Phức tạp hơn | Production |

**Recommendation:** Dùng strategy **Multi Models + Multi Keys** (đang implement) để đảm bảo pipeline chạy liên tục 24/7.

## 🎯 Best Practices

1. ✅ **Luôn cấu hình ít nhất 2 API keys**
2. ✅ **Để mặc định MODEL_PRIORITY** (đã tối ưu)
3. ✅ **Kiểm tra quota trước khi chạy lớn**: https://aistudio.google.com
4. ✅ **Chạy thử với 10-20 ảnh trước** để test strategy
5. ✅ **Backup checkpoint file** định kỳ
6. ✅ **Monitor logs** để điều chỉnh kịp thời

---

**Chiến lược này đảm bảo pipeline của bạn chạy mượt mà, tối ưu quota và xử lý mọi tình huống lỗi một cách thông minh!** 🚀
