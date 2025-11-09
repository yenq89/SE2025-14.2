# Báo cáo tiến độ - Tuần 1

## Tóm tắt
Tuần đầu, nhóm xác định sẽ sử dụng mã nguồn mở Stable Diffusion (từ Hugging Face) làm nền tảng cho đề tài: xây dựng hệ thống AI vẽ tranh. Nhóm thử nghiệm một số phiên bản để khảo sát khả năng: Stable Diffusion XL base v1.0, SD v1.5 và SD v3.5 large.

## Hoạt động đã thực hiện
- Phân công ban đầu: chia 3 phiên bản mô hình cho 3 thành viên để chạy thử và so sánh kết quả.
- Mỗi thành viên lựa chọn chủ đề ảnh thử nghiệm riêng:
  - Thành viên 1: hình ảnh người nông dân (theo phong cách anime).
  - Thành viên 2: thú cưng theo phong cách anime.
  - Thành viên 3: tranh sơn mài, hoa sen Việt Nam.
- Tìm hiểu tài nguyên mã nguồn (checkpoints) và công cụ (Hugging Face, diffusers, các repo hỗ trợ DreamBooth/LoRA).

## Vấn đề gặp phải
- Hạ tầng: máy tính cá nhân và Google Colab miễn phí gặp hạn chế GPU/VRAM, dẫn đến quá trình cài đặt và thử nghiệm không suôn sẻ.

## Phân tích và quyết định tạm thời
- Vì giới hạn tài nguyên (chưa mượn được GPU từ thầy), tất cả các thử nghiệm hiện chỉ chạy trên Google Colab thuộc máy cá nhân. Do đó nhóm chưa chốt lựa chọn model để fine‑tune.
- Nhóm sẽ tiếp tục ghi chép các lỗi, kết quả thử nghiệm trên Colab và chủ động xin quyền truy cập GPU mạnh hơn để thực hiện các thử nghiệm có VRAM lớn hơn và quyết định baseline cuối cùng.

## Kế hoạch tiếp theo (Tuần 2)

Cả phiên bản và dữ liệu đang được nhóm tìm hiểu để chọn ra hướng đi có tiềm năng nhất. Dự kiến kế hoạch tuần tới bao gồm những công việc sau:
- Chuẩn bị dataset: ảnh + caption kèm theo
- Thử chạy LoRA nhỏ trên tập con (Colab) để kiểm tra pipeline.
- Chuẩn bị yêu cầu truy cập GPU và môi trường để huấn luyện quy mô lớn khi có GPU.
