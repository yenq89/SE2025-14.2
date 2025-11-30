# Báo cáo công việc tuần 5 — Dự án LoRA Ghibli SD

## 1. Tổng quan
Nhóm đã huấn luyện model với bộ dữ liệu gồm 4,776 ảnh và đoạn text caption. 

Xử lý một vài vấn đề liên quan đến dữ liệu, quá trình test mô hình (#17, #20, #23)

## 2. Kết quả huấn luyện

Mô hình đã bắt đầu tạo ra các nhân vật mang phong cách Ghibli. Tuy nhiên, chất lượng vẫn chưa đạt mong đợi. Một số hạn chế ghi nhận được:

- Chi tiết khuôn mặt bị mất hoặc thể hiện thiếu rõ ràng.

- Nét vẽ tóc và trang phục có hơi hướng phong cách Ghibli Studio nhưng còn mờ nhạt, thiếu độ chính xác.

- Một số góc mặt cho kết quả bị nhiễu hoặc không nhất quán.
Một vài ví dụ:

<p float="left">
  <img src="D:\SE\SE2025-14.2\test\images\v2\modified_test_4.png" width="200" />
  <img src="D:\SE\SE2025-14.2\test\images\v2\modified_test_5.png" width="200" />
  <img src="D:\SE\SE2025-14.2\test\images\v2\modified_test_6.png" width="200" />
</p>

**Nguyên nhân có thể do:**
- Mô hình bị overfitting
- Ảnh huấn luyện nhân vật không có đủ chi tiết trên khuôn mặt
- Caption chưa mô tả đầy đủ sự khác biệt giữa các góc mặt: Bộ ảnh có nhiều góc chụp khác nhau nhưng phần caption chưa thể hiện rõ, dẫn đến mô hình khó phân biệt và bị nhiễu trong quá trình học.

## 3. Ý tưởng khắc phục dữ liệu 
- Loại bỏ ảnh có nhiều nhân vật
- Loại bỏ ảnh nhân vật bị mất chi tiết mắt, mũi, miệng. . .
- Loại bỏ ảnh nhân vật chỉ có bóng lưng
- Loại bỏ ảnh nhân vật quá nhỏ so với khung cảnh xung quanh
- Giữ tỉ lê nhân vật so với khung hình ổn định

Ngoài ra, cần có phương pháp để theo dõi mô hình học đến bước nào sẽ bắt đầu đủ tốt, đến bước nào sẽ xấu dần đi.
Số lượng ảnh lên tới 4,776 ảnh gây tốn kém trong quá trình huấn luyện, mất tới hai ngày để mô hình có thể học xong.
---