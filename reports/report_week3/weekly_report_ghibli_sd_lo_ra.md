# Báo cáo công việc tuần 3 — Dự án LoRA Ghibli SD

## 1. Tổng quan
Nhóm đã huấn luyện model với bộ dữ liệu gồm 171 ảnh và đoạn text caption. Các ảnh được craw về máy bằng `simple_image_download`, text caption được tạo bằng BLIP.

---


## 2. Quá trình thu thập dữ liệu

Sau khi thử nghiệm nhiều hướng, nhóm quyết định sử dụng **thư viện `simple_image_download` (simp)** vì các lý do:
- Không cần xác thực API.
- Tốc độ tải cao, dễ thao tác.
- Hỗ trợ tự động lưu và đặt tên file theo keyword.

#### Từ khóa tìm kiếm
Mỗi nhân vật được tìm bằng cấu trúc:
```
<Character> from <Movie> Studio Ghibli
```
Ví dụ: `Howl Jenkins Pendragon from Howl’s Moving Castle Studio Ghibli`

Sau khi tải về, toàn bộ ảnh từ các nhân vật đều được lưu chung vào một thư mục duy nhất:
```
/data/ghibli/
 ├── 1.jpg
 ├── 2.jpg
 ├── 3.jpg
 └── ...
```

Để đảm bảo chất lượng ảnh đầu vào:
- Ảnh được **chuyển về RGB**, **resize về 512×512** (chuẩn SD1.5).
- Loại bỏ ảnh trùng, ảnh chứa text.
- Bỏ qua ảnh lỗi (không mở được hoặc không đúng định dạng).

Tất cả dữ liệu cuối cùng được gom lại trong folder `/ghibli/` duy nhất để thuận tiện cho pipeline training.

---

## 3. Sinh caption tự động bằng BLIP

Sau khi hoàn tất bước lọc ảnh, nhóm tiến hành gán nhãn mô tả cho từng ảnh bằng **mô hình BLIP (Salesforce/blip-image-captioning-large)**. 

### Quy trình:
1. Load mô hình BLIP từ HuggingFace.
2. Duyệt toàn bộ folder `/ghibli/`.
3. Sinh caption tự động cho từng ảnh.
4. Lưu caption và ảnh vào file .jsonl.


## 4. Thử nghiệm training với Diffusers

### Cấu hình:
- Mô hình gốc: `runwayml/stable-diffusion-v1-5`
- Framework: `HuggingFace Diffusers`
- Dataset: `/data/ghibli/`


### Thiết lập môi trường GPU 
- GPU: NVIDIA RTX 3090 (mượn từ giảng viên), chạy đa GPU.
- Tùy chọn cấu hình khi thiết lập `accelerate` (theo hướng dẫn của Diffusers):
  - Môi trường chạy: This machine (ASUS)
  - Loại máy: multi-GPU
  - Số máy: 1
  - Kiểm tra lỗi phân tán trong khi chạy: no
  - Tối ưu bằng Torch Dynamo: no
  - DeepSpeed: no
  - FullyShardedDataParallel (FSDP): no
  - Megatron-LM: no
  - Số GPU dùng cho training phân tán: 2
  - Danh sách GPU dùng: all
  - Bật NUMA efficiency (NVIDIA): yes
  - Mixed precision: fp16
- Cấu hình được lưu tại: `C:\Users\ssm_d\.cache\huggingface\accelerate\default_config.yaml`

```bash
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export DATASET_NAME="/mnt/c/Users/SE2025-14.2/data/ghibli"

accelerate launch --num_processes=1 --mixed_precision="no" train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --dataset_name=$DATASET_NAME \
  --caption_column="text" \
  --resolution=512 \
  --random_flip \
  --train_batch_size=1 \
  --num_train_epochs=100 \
  --checkpointing_steps=5000 \
  --learning_rate=1e-04 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --seed=42 \
  --output_dir="/mnt/c/Users/ssm_d/SE2025-14.2/model" \
  --validation_prompt="cute dragon creature" \
  --report_to="wandb"
```

Giải thích các đối truyền vào:

```bash 
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export DATASET_NAME="/mnt/c/Users/SE2025-14.2/data/ghibli"
```

Đặt biến môi trường trỏ đến mô hình nền (base model) của Stable Diffusion.
Model SD 1.5 được tải từ Hugging Face.
Link đến dataset 

```bash
--num_processes=1 --mixed_precision="no"
```

Huấn luyện bằng 1 process: Đang tạm để là 1 vì khi cho số process lớn hơn thì khi huấn luyện bị lỗi "Out of memory"

Không dùng mixed precision (fp16/bf16).

```bash 
train_text_to_image_lora.py
```
Script chính để huấn luyện LoRA từ thư viện HuggingFace Diffusers.

```bash
--pretrained_model_name_or_path=$MODEL_NAME
```
Đường dẫn mô hình gốc để fine-tune.
Lấy từ biến MODEL_NAME đã export ở trên.

```bash 
--caption_column="text"
```
Cột chứa caption mô tả ảnh trong dataset.

```bash 
--resolution=512
```
Tất cả ảnh sẽ được resize thành 512×512 trước khi training.

```bash 
--random_flip
```
Enable random horizontal flip data augmentation khi training.

```bash 
--train_batch_size=1
```
Batch size = 1

```bash 
--num_train_epochs=100
```
Số epoch huấn luyện = 100.

```bash 
--checkpointing_steps=5000
``` 
Cứ mỗi 5000 step sẽ lưu checkpoint LoRA.

```bash 
--learning_rate=1e-04
``` 
Learning rate = 0.0001
LR phổ biến khi train LoRA.

```bash 
--lr_scheduler="constant"
```
Không giảm learning rate theo thời gian.

```bash 
--lr_warmup_steps=0
```
Không dùng warmup cho learning rate.

```bash 
--seed=42
```
Set random seed giúp tái tạo kết quả.

```bash 
--output_dir="/mnt/c/Users/ssm_d/SE2025-14.2/model"
```
Thư mục lưu model LoRA đầu ra.

```bash 
--validation_prompt="a girl in pink dress in Ghibli style"
```
Mỗi lần checkpoint, script sẽ sinh ảnh kiểm tra (validation image) bằng prompt này.

```bash 
--report_to="wandb"
```
Ghi log training lên Weights & Biases (W&B): Loss, Learning Rate, Validation Images, Checkpoints

Muốn tắt thì đặt:

```bash 
--report_to="none"
```
## 5. Kết quả
Mô hình được huấn luyện thành công, có thể sinh ảnh từ text, chạy được trên giao diện web.

Ví dụ: Với 3 câu lệnh lần lượt là

1, "A cheerful young boy smiling happily in Ghibli style"

2, "A cute dog in Ghibli anime style, playing with a baseball"

3, "A 7 years old girl wearing pink dress in Ghibli studio anime style"

Thì 3 ảnh được mô hình gốc stable-diffusion-v1-5 tạo ra là:
<p float="left">
  <img src="D:\SE\SE2025-14.2\reports\report_week3\image_gen_from_sd15\1.png" width="200" />
  <img src="D:\SE\SE2025-14.2\reports\report_week3\image_gen_from_sd15\2.png" width="200" />
  <img src="D:\SE\SE2025-14.2\reports\report_week3\image_gen_from_sd15\3.png" width="200" />
</p>

Mô hình mới được huấn luyện với bộ data Ghibli tạo được ba ảnh: 

<p float="left">
  <img src="D:\SE\SE2025-14.2\reports\report_week3\image_gen_from_lora_ghibli\1.png" width="200" />
  <img src="D:\SE\SE2025-14.2\reports\report_week3\image_gen_from_lora_ghibli\2.png" width="200" />
  <img src="D:\SE\SE2025-14.2\reports\report_week3\image_gen_from_lora_ghibli\3.png" width="200" />
</p>

**Nhận xét chung:** Mô hình chưa sinh ảnh được như đúng mong đợi
Nguyên nhân có thể do bộ data chưa thực sự tốt do hạn chế về số lượng hình ảnh và caption cho mỗi ảnh được gen từ BLIP quá ngắn, thiếu mô tả cụ thể.

## 6. Tổng kết
Trong tuần 3, nhóm đã hoàn thành toàn bộ pipeline huấn luyện LoRA Ghibli dựa trên Stable Diffusion 1.5, bao gồm các bước thu thập dữ liệu, xử lý ảnh, sinh caption tự động và triển khai huấn luyện bằng Diffusers. Mặc dù mô hình đã được train thành công và có thể sinh ảnh đúng với nội dung prompt, nhưng chất lượng hình ảnh vẫn chưa đạt được phong cách Ghibli như mong muốn.

Nguyên nhân chính được xác định gồm:

- Số lượng và chất lượng dataset còn hạn chế (chỉ 171 ảnh, nhiều ảnh nhiễu hoặc không đồng nhất phong cách).

- Caption từ BLIP quá đơn giản, không mô tả rõ đặc điểm nhân vật, bối cảnh hoặc phong cách nghệ thuật.

- Chưa tối ưu đầy đủ hyperparameter (batch size thấp, không dùng mixed precision, số epoch lớn nhưng chất lượng dữ liệu chưa đủ mạnh).

Tuy vậy, việc thiết lập được pipeline hoàn chỉnh từ thu thập dữ liệu đến huấn luyện LoRA là một kết quả quan trọng. Đây là nền tảng để nhóm tiếp tục cải thiện chất lượng mô hình trong các tuần tiếp theo thông qua: mở rộng dataset, viết caption thủ công/chuẩn hóa mô tả, tinh chỉnh hyperparameter, và thử nghiệm phương pháp training mạnh hơn.
