# Báo cáo công việc tuần qua — Dự án LoRA Ghibli SD

## 1. Tổng quan
Qua các thử nghiệm ban đầu trên Colab và máy cá nhân để so sánh các phiên bản Stable Diffusion, nhóm đã thống nhất chốt đề tài: **Tạo ảnh phong cách Ghibli bằng mô hình Stable Diffusion (LoRA)**. Sau khi đánh giá sơ bộ, nhóm chọn checkpoint SD v1.5 làm baseline để tiếp tục thử nghiệm LoRA và fine‑tune.

Trong tuần vừa qua, nhóm tập trung vào giai đoạn **chuẩn bị dữ liệu huấn luyện** và **thử nghiệm pipeline training với thư viện Diffusers của Hugging Face**. Mục tiêu của tuần là tạo được dataset gồm các nhân vật trong các bộ phim Ghibli với caption tự động, phục vụ cho quá trình fine-tune mô hình SD v1.5.

---

## 2. Quá trình thu thập dữ liệu

### 2.1. Thử nghiệm các nguồn crawl
Ban đầu, nhóm thực hiện thử nghiệm crawl ảnh nhân vật Ghibli từ nhiều nguồn công khai nhằm tối ưu độ đa dạng và chất lượng hình ảnh.

#### a. TMDB API
- **Mục đích:** lấy danh sách phim và nhân vật chính thức của Studio Ghibli.  
- **Kết quả:** chủ yếu truy xuất được metadata (poster, mô tả phim); ảnh nhân vật có số lượng ít và phần lớn trùng lặp (do nhiều người dùng upload lại nội dung tương tự).  
- **Lý do không tiếp tục:** nguồn ảnh nhân vật từ TMDB không đủ đa dạng/chất lượng cho mục tiêu huấn luyện nhân vật riêng biệt; nền tảng không cung cấp endpoint chuyên biệt cho ảnh nhân vật.

#### b. DuckDuckGo Image Search
- **Mục đích:** sử dụng truy vấn tự động để lấy hình từ các nguồn an toàn (Wikipedia, fandom, IMDb, ghibli.jp,...).  
- **Công cụ:** thư viện `duckduckgo-search`.  
- **Vấn đề gặp phải:** DuckDuckGo nhanh chóng trả lỗi **403 Ratelimit** sau vài lượt tìm kiếm đầu tiên do chặn truy vấn tự động.  
- **Kết luận:** tốc độ và độ ổn định không đảm bảo.

#### c. Wikimedia Commons API
- **Mục tiêu:** lấy ảnh chính thống, bản quyền tự do.  
- **Vấn đề:** yêu cầu xác thực truy cập và bị lỗi 403 Forbidden khi gửi request từ môi trường Colab.  
- **Kết luận:** không khả thi cho tự động hóa quy mô lớn.

### 2.2. Chọn phương án chính thức — `simple_image_download`
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

### 2.3. Lọc và xử lý dữ liệu hình ảnh
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
4. Lưu caption theo 2 định dạng:
   - Tất cả caption được tổng hợp vào file `captions.txt` trong cùng folder.
   - Tương tự nhưng là với file `captions.csv` trong cùng folder.

### Lưu ý quan trọng:
- Caption tránh chứa **tên nhân vật hoặc tên phim** để giảm bias khi train LoRA.
- Ưu tiên mô tả rõ: **giới tính/chủ thể** (ví dụ: young girl/boy), **trang phục** (màu sắc cụ thể: yellow dress), **hành động/tư thế**, và **bối cảnh** (forest, town, room) theo phong cách Ghibli. Có thể bổ sung ánh sáng/màu sắc chi tiết khi phù hợp.

Ví dụ caption:
> "a young girl in a yellow dress stands in front of a forest in Ghibli style"

---

## 4. Thử nghiệm training với Diffusers

### Cấu hình:
- Mô hình gốc: `runwayml/stable-diffusion-v1-5`
- Framework: `HuggingFace Diffusers`
- Dataset: `/data/ghibli/`

### Thử nghiệm inference bằng giao diện web — AUTOMATIC1111 (stable-diffusion-webui)
- Nhóm có clone và chạy thử giao diện web mã nguồn mở **stable-diffusion-webui** (thường gọi là webui của AUTOMATIC1111) để kiểm tra nhanh chất lượng prompt và quản lý LoRA.
- Nguồn gốc: dự án cộng đồng trên GitHub do tài khoản AUTOMATIC1111 do một người Việt Nam khởi xướng và duy trì cùng rất nhiều contributor. Webui cung cấp giao diện đồ họa để sinh ảnh, inpainting, quản lý model/LoRA/embedding, và nhiều extension.
- Lý do sử dụng: thao tác trực quan, dễ bật tắt LoRA/checkpoint, so sánh đầu ra với cùng prompt; thích hợp cho bước thử nghiệm nhanh bên cạnh pipeline Diffusers.

### Thiết lập môi trường GPU (Hugging Face Accelerate)
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

### Kết quả:
Trong quá trình chạy script `train_text_to_image_lora.py`, xảy ra lỗi:
```
ValueError: --caption_column value '{args.caption_column}' needs to be one of: image, text
```

### Phân tích lỗi:
- Nguyên nhân: cấu trúc dataset không khớp định dạng yêu cầu của Diffusers (`image` và `text` column trong CSV hoặc dataset format của HuggingFace Datasets`).
- Giải pháp đang thực hiện:
  - Chuyển định dạng dữ liệu sang chuẩn CSV với cột `image` và `text`.
  - Kiểm tra lại pipeline nạp dữ liệu trong `train_text_to_image_lora.py`.
  - Đồng bộ hóa đường dẫn file ảnh và caption.

---

## 5. Định hướng tuần tới
- Hoàn thiện patch dataset để tương thích hoàn toàn với Diffusers.
- Kiểm tra tốc độ huấn luyện trên GPU và xác minh chất lượng ảnh sinh ra sau fine-tune.
- Tinh chỉnh dataset (dự kiến thực hiện trong tuần tới):
  - Rà soát và loại trùng (MD5/perceptual hash); loại bỏ ảnh mờ, out-of-focus, ảnh chứa text/watermark/logo.
  - Cân bằng chủ đề/nhân vật (nếu có), tránh lệch phân phối (ví dụ cân bằng giới tính/bối cảnh chính).
  - Chuẩn hóa caption: không chứa tên riêng; tăng tính mô tả về giới tính/chủ thể, bối cảnh, và màu sắc chi tiết.
  - Chuẩn hóa tên file; đồng bộ cặp image <-> caption; cập nhật `captions.csv` chuẩn cột `image`,`text`.
- Chuẩn bị visualization để đưa vào báo cáo cuối kỳ.

---

## 6. Tổng kết
Tuần qua, nhóm đã:
- Thử nghiệm và đánh giá nhiều API để thu thập dữ liệu ảnh Ghibli.
- Chọn được pipeline crawl nhanh và hiệu quả bằng `simple_image_download`.
- Hoàn thiện bước sinh caption tự động bằng BLIP.
- Bắt đầu thử nghiệm huấn luyện LoRA bằng Diffusers, hiện đang xử lý lỗi cấu trúc dataset.

Kết quả này là nền tảng quan trọng để bước sang giai đoạn fine-tuning mô hình trong tuần tới.

