# SE2025-14.2

--- 
# Dự án môn học Công Nghệ Phần Mềm - Vẽ tranh nhân vật theo phong cách Ghibli studio

---

Dự án SE2025-14.2 nhằm xây dựng một hệ thống sinh ảnh nhân vật theo phong cách Studio Ghibli dựa trên mô hình Stable Diffusion, kết hợp với kỹ thuật LoRA (Low-Rank Adaptation) để fine-tune mô hình trên tập dữ liệu phong cách chuyên biệt.

Hệ thống bao gồm:

- Pipeline huấn luyện LoRA cho Stable Diffusion

- WebUI cho phép người dùng nhập prompt, điều chỉnh tham số và sinh ảnh trực tiếp trên trình duyệt

Video demo: [Video](https://drive.google.com/drive/folders/1u-tl908jZOr40UpcrJfGtpwYFckIpD16?usp=drive_link)

## Hướng dẫn các bước thực hiện 

---

### 1. Thu thập dữ liệu
Dữ liệu huấn luyện được thu thập thông qua các phương pháp crawl ảnh từ nhiều nguồn khác nhau trên Internet. 

Sau đó tiến hành các bước xử lý:

1. Lọc bỏ ảnh lỗi, ảnh không phù hợp bằng cách thủ công
2. Sinh mô tả tự động cho ảnh
3. Chuẩn hoá kích thước ảnh
4. Chuẩn hoá định dạng dữ liệu phục vụ huấn luyện 

Dữ liệu huấn luyện được tổ chức như sau:

```
data/
└── name_of_data_folder/
    └── train/
        ├── 0001.jpg
        ├── 0002.jpg
        ├── ...
        └── metadata.jsonl
```

**Một dòng mẫu từ file `metadata.jsonl`:**

```json
{"file_name": "0001.jpg", "text": "a young girl in a yellow shirt and orange skirt is walking through a field in Ghibli style"}
```
**Lưu ý:** Cần thực hiện đúng cách tổ chức này để có thể tương thích với thư viện và chạy chương trình huấn luyện.

Chi tiết về oông cụ, phương pháp xem tại: [Hướng dẫn dùng công cụ AI xử lý ảnh](https://github.com/yenq89/SE2025-14.2/tree/main/data_processing)

Có thể tìm thấy dữ liệu ở: [Bộ dữ liệu Ghibli 5 version](https://drive.google.com/drive/folders/1DGaIaaheG0nU-IE9M8bDV1c_4JN1fuE-?usp=drive_link)

### 2. Huấn luyện mô hình

Trước khi chạy các script huấn luyện, cần cài đặt đầy đủ các thư viện cần thiết.

Khuyến nghị cài đặt `diffusers` từ source để đảm bảo tương thích với các script mới nhất:

```bash
git clone https://github.com/huggingface/diffusers
cd diffusers
pip install .
```

Sau đó, di chuyển vào folder example và cài đặt các dependency bổ sung

```bash
pip install -r requirements.txt
```

Tiếp theo, khởi tạo môi trường Accelerate

```bash
accelerate config
```

**Huấn luyện với LoRA**

LoRA (Low-Rank Adaptation) là phương pháp fine-tune mô hình Stable Diffusion bằng cách chỉ huấn luyện một số lớp trọng số nhỏ được thêm vào mô hình gốc, trong khi giữ nguyên các trọng số ban đầu. Cách tiếp cận này giúp giảm số lượng tham số cần huấn luyện, tiết kiệm tài nguyên.

Nhờ LoRA, Stable Diffusion có thể được fine-tune trên tập dữ liệu tùy chỉnh ngay cả trên các GPU phổ thông, đồng thời các trọng số LoRA có kích thước nhỏ, dễ dàng lưu trữ và chia sẻ.

Để huấn luyện LoRA Ghibli trên tập dữ liệu đã được thu thập trước đó. Đầu tiên, ta khai báo biến môi trường:

```bash
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export DATASET_NAME="/mnt/c/Users/SE2025-14.2/data/ghibli"
```

Bắt đầu huấn luyện:

```bash
accelerate launch --mixed_precision="fp16" train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --dataset_name=$DATASET_NAME \
  --caption_column="text" \
  --resolution=512 \
  --random_flip \
  --train_batch_size=1 \
  --num_train_epochs=100 \
  --checkpointing_steps=5000 \
  --learning_rate=1e-4 \
  --output_dir="output_models" \
  --validation_prompt="Ghibli style a young girl with brown hair tied back, wearing a simple red dress" \
  --report_to="wandb"
```
Các đối số truyền vào có thể được thay đổi tuỳ theo mục đích.

Trong quá trình huấn luyện. mô hình sẽ sinh ảnh mẫu để đánh giá và ghi log lên Weight&Biases

File trọng số LoRA sau khi huấn luyện có kích thước rất nhỏ, tiện cho việc lưu trữ và chia sẻ.

### 3. Chạy mô hình trên WebUI

Sau khi huấn luyện xong, các checkpoint được lưu trong thư mục ```output_models```. Muốn sử dụng checkpoint nào thì đưa file ```pytorch_lora_weights.safetensor``` vào folder ```software_product/model```

Để chạy WebUI, di chuyển vào thư mục ```software_product/backend```, rồi sau đó khởi động server:

```bash
app --reload --host 127.0.0.1 --port 8000
```
Giao diện WebUI 

<img width="1590" height="820" alt="image" src="https://github.com/user-attachments/assets/5f2bd21b-38e1-41a5-a028-4afc3191447b" />

Các bước sử dụng:

1. Chọn model LoRA

2. Nhập prompt mô tả ảnh mong muốn

3. Điều chỉnh các tham số (nếu cần)

4. Nhấn Generate để sinh ảnh

Kết quả ảnh sẽ được hiển thị trực tiếp trên trình duyệt.

> ⚠️ **Lưu ý quan trọng:**  
> Mô hình này **chỉ phục vụ mục đích học tập và nghiên cứu** trong khuôn khổ môn học SE2025-14.2.  
> Việc sử dụng dữ liệu tranh của Studio Ghibli trong huấn luyện AI có thể gây **các tranh cãi liên quan bản quyền**.  
> **không nên sử dụng mô hình này cho mục đích thương mại hoặc phân phối**.
