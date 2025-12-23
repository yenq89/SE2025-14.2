# Báo cáo công việc tuần 7 - Dự án LoRA Ghibli SD

## Mục tiêu tuần:
- [x] Tìm ra bộ tham số phù hợp.
- [x] Tìm ra mô hình tốt nhất và bộ dữ liệu tương ứng.

## Hành động:
- Code mã lệnh huấn luyện LoRA và chạy chương trình.
- Kết nối và tải thông tin tiến trình huấn luyện lên WanDB.
- Đánh giá biểu đồ kết quả.
- Đánh giá ảnh test cũng như ảnh validation.
- Trình bày, báo cáo từng lần chạy (config) vào các issues https://github.com/yenq89/SE2025-14.2/issues/31 và https://github.com/yenq89/SE2025-14.2/issues/32.
- Theo dõi, đề xuất và rút ra các thông tin quan trọng (issues https://github.com/yenq89/SE2025-14.2/issues/31, https://github.com/yenq89/SE2025-14.2/issues/32 và https://github.com/yenq89/SE2025-14.2/issues/34).
- Lặp lại quá trình thử nghiệm với các bộ thông số khác.
- Sau đó, thực hiện test độc lập từng mô hình với bộ dữ liệu test đã được chọn lọc ở issue https://github.com/yenq89/SE2025-14.2/issues/35.
- Tổng hợp kết quả để tìm ra mô hình tốt nhất.

## Phân công công việc:
- Huấn luyện mô hình với dữ liệu **ver3**: Yến.
- Huấn luyện mô hình với dữ liệu **ver4**: Yến (bản 4.1 - không trình bày trong https://github.com/yenq89/SE2025-14.2/issues/32) và Minh (các bản được trình bày trong https://github.com/yenq89/SE2025-14.2/issues/32).
- Huấn luyện mô hình với dữ liệu **ver5**: Yến và Minh.
- Đánh giá biểu đồ: Yến và Minh.
- Đánh giá ảnh: Yến và Minh.
- Báo cáo vào issue: Yến và Minh.
- Test độc lập: Yến, Phương và Minh.
- Trình bày báo cáo tuần: Minh.

## Đánh giá tổng quan kết quả thu được từ https://github.com/yenq89/SE2025-14.2/issues/31 và https://github.com/yenq89/SE2025-14.2/issues/32:

Đánh giá bao gồm hai phần: 
- Đánh giá theo hàm loss.
- Đánh giá theo ảnh validation và ảnh test.

### Dựa theo hàm loss.
Hàm loss có tên đầy đủ là: **Noise Prediction Loss**, thường được tính theo dạng **Mean Squared Error**. Ảnh đầu vào sẽ được nén về dạng $z_0$, văn bản đầu vào được mã hóa thành $c$. Hệ thống sẽ sử dụng một tấm nhiều $\epsilon$ để trộn vào $z_0$ tạo thành ảnh nhiễu $z_i$. Mô hình sẽ phải đoán giá trị của tấm nhiễu $\epsilon_{pred}$ rồi so sánh với tấm nhiễu thực tế $\epsilon$. Kết quả loss thu được tính theo công thức sau:

$Loss = ||\epsilon - \epsilon_{pred}||^2$

- Khi loss thấp, model đoán nhiễu chính xác $\rightarrow$ Khử nhiễu tốt $\rightarrow$ Tạo ra ảnh đẹp, đúng prompt.
- Khi loss cao = Model đoán sai $\rightarrow$ Ảnh ra lò sẽ bị nhòe hoặc không đúng hình dạng.

Kết quả của hàm loss phản ánh khả năng:
- Hiểu cấu trúc của hình ảnh của mô hình.
- Học được cách liên kết từ ngữ với hình ảnh.

<img width="2528" height="1328" alt="528842290-aa792de8-4765-44ac-8284-5238deabe5d4" src="https://github.com/user-attachments/assets/2afc898d-c113-43ac-a73a-4a770303e334" />

(Ảnh thuộc **Config 01** của https://github.com/yenq89/SE2025-14.2/issues/32)

- Tổng quan, giá trị *smooth loss* khi train trên dữ liệu **ver 3** và **ver 4** đều giao động trong khoảng `0.11 - 0.13`. Đây là giá trị nhỏ, cho thấy mô hình đã hiểu tương đối tốt về cấu trúc hình ảnh và liên kết từ ngữ-hình ảnh. Tuy nhiên, giá trị này lại có xu hướng đi ngang chứ không thể giảm cho thấy mô hình gặp khó khăn trong việc tìm ra các điểm cực tiểu cục bộ, hay nói cách, mô hình có vẻ gặp khó khăn để cải thiện.
- Một vấn đề khác được trình bày là hình dáng của đường loss (cả *smooth loss* và *batch loss*) là giống nhau giữa các lần huấn luyện độc lập. Một phần, tham số sử dụng chung `seed=42` nên việc chọn batch, cách hình thành lớp nhiễu là giống nhau ở từng bước. Tuy nhiên, việc các mô hình có chung tham số ngoại trừ khác `learning_rate` cho thấy một giả định, các thông tin quá nhỏ đã bị triệt tiêu do làm tròn, khi mô hình sử dụng `fp16`. Ví dụ như hình ảnh trên, thuộc **Config 01**, ta có thể sử dụng biểu đồ này để đại diện cho train loss của **Config 03**, **Config 05**, **Config 06** và **Config 07**.
- Một thông tin khác là, dựa vào độ lớn của batch (`batch_size`), có thể thấy ở đa số các bước lặp liên tiếp đủ để mô hình duyệt qua hết toàn bộ dữ liệu, luôn có những *batch loss* cao và điều này diễn ra phổ biến. Điều này cho thấy mô hình không cải thiện kết quả học, hoặc mô hình học được điều mới nhưng lại quên đi những thông tin khác. Đó sẽ là điều tốt nếu mô hình học được các thông tin quan trọng, phù hợp và quên đi một số thông tin cũ không liên quan đến phong cách Ghibli.
- Ngoài ra, nhắc đến `batch_size`, việc giảm từ `8` xuống `4`, dù dự kiến sẽ làm tăng nhiễu dữ liệu quá lớn, thực tế không làm tăng nhiễu dựa theo kết quả đã thu được (**Config 02** của https://github.com/yenq89/SE2025-14.2/issues/32), và việc tăng từ `8` lên `16` (**Config 04**) đã làm mô hình học nhầm, khi xuất hiện các ảnh có nhiều ngón tay, dị thường.

### Dựa theo ảnh sinh ra khi và sau khi huấn luyện:
Ngoài theo dõi qua dữ liệu *loss*, ảnh sinh ra cũng rất quan trọng, nó phản ánh liệu mô hình có sinh ra những hình ảnh mà con người mong muốn, gây ấn tượng, hay chỉ có thể học theo một cách máy móc. Bản thân mỗi thành viên trong nhóm đã có quan niệm khác nhau về vẻ đẹp, sự phù hợp khi đối chiếu với mục tiêu tạo ra ảnh mang phong cách Ghibli. Vì vậy, không có quy chuẩn cụ thể mà phụ thuộc vào cảm nhận của mỗi người. Điều này đặc biệt quan trọng khi cung cấp **đa dạng góc nhìn**, nhất là khi mô hình chỉ đang cung cấp góc nhìn của nó, và dựa theo đó để cố gắng cải thiện.

<img width="312" height="311" alt="527622863-0d313cba-ac5d-4b09-b025-0a4750e8384a" src="https://github.com/user-attachments/assets/92c3a208-6e70-4e77-8d1a-8ba855bf1d9e" />

- Trái ngược với việc *train loss* giao động, ảnh sinh ra cho thấy sự cải thiện của mô hình khi học được nét vẽ. Ảnh ở những step sau tương đối tốt, ít hình ảnh bị mất chi tiết, hoàn chỉnh.
- Tuy nhiên, điều đó không đúng với mọi mô hình, có những mô hình có khả năng học kém, kết quả sinh ra có điểm dị thường, mờ, méo mó, ... Các lỗi thường gặp xuất hiện ở khuôn mặt (mắt, cằm, má, miệng, ...), tóc, cánh tay, bàn tay và phần chân. Nhiều hình ảnh không có kích cỡ cơ thể nhân vật phù hợp.
- Việc hiểu ngữ cảnh cũng là hạn chế, khi mô hình gặp khó khăn khi vẽ lại ảnh có *caption* được thay đổi dù chỉ một chút so với *caption* gốc, hoặc thậm chí là *caption* từ dữ liệu huấn luyện. Lần chạy với sự bổ sung cụ thể `rank=32` đã cải thiện điều đó màu sắc hình nền và quần áo nhân vật đúng với mô tả hơn.
- Đối với các lần train có tham số `learning_rate` lớn, mô hình học và cải thiện rất nhanh nhưng đôi khi thiếu đi chiều sâu. Trong khi đó, tham số `learning_rate` nhỏ cho thấy sự cải thiện từng bước của mô hình, nhưng đồng thời, mô hình khó có thể sửa những lỗi lớn hay những lỗi yêu cầu nhiều lần cải thiện. Việc cài dặt `lr_scheduler="linear"`chưa thực sự cho thấy thay đổi đáng kể khi train.
- Lần chạy `rank=32` đã cho thấy nhiều sự cải thiện về hình nét của nhân vật.
- Việc tăng `num_validation_images` lên `8` hoặc `10` giúp cải thiện việc đánh giá kết quả ngay tại thời điểm mô hình chạy.

### Dựa theo đánh giá ảnh test.
Chi tiết nội dung test: *caption* và tiêu chí đánh giá được trình bày ở https://github.com/yenq89/SE2025-14.2/issues/35.
| Phiên bản | Kết quả tốt nhất | Checkpoint tương ứng |
| --------- | ---------------- | -------------------- |
| 3.1 | 7/20 | 3000 |
| 3.2 | 7-8/20 | 2000 |
| 3.3 | 6/20 | 4000 |
| 4.1 | 3/20 | 15000 |
| 4.2 | 8/20 | 1500 |
| 4.3 | 8/20 | 1500, 5000, 5500 |
| 4.4 | 10/20 | 1500 |
| 4.5 | 12/20 | 2000 |
| 4.6 | 9-10/20 | 2500 |
| 4.7 | 3/20 | 1500 |
| 4.8 | 14/20 | 1500 |
| 4.9 | 10/20 | 1500 |
| 5.0 | 5/20 | 2000 |
| 5.1 | 8/20 | 1000 |

- Mặc dù đây là kết quả được đánh giá chủ quan bởi cả ba thành viên, kết quả nổi bật của mô hình thường nằm ở khoảng 3000 step đầu tiên.
- Các mô hình có kết quả nổi bật là `3.2`, `4.4`, `4.5`, `4.6`, `4.8`, `4.9` và `5.1`.

## Tổng kết
### Quá trình huấn luyện:
Như vậy, nhóm đã tìm ra các kết quả vô cùng tích cực. Trả lời câu hỏi:
- Bộ tham số tốt nhất bao gồm: `batch_size=8`, `learning_rate` bằng `1e-4` hoặc `5e-5`.
- Mô hình tốt nhất có lẽ là `4.8` tương ứng với điểm `14/20` và thuộc bộ dữ liệu **ver 4**.

### Những công việc khác đã hoàn thành trong thời gian này: 

1. Xử lý & Nâng cao Chất lượng Dữ liệu
* **Cải thiện Data:** Thực hiện nâng cao chất lượng bộ dữ liệu huấn luyện (Data quality improvement).
* **Trực quan hóa:** Tối ưu hóa phần trình bày các biểu đồ trực quan để theo dõi dữ liệu tốt hơn.
* **Xử lý ngôn ngữ:** Khắc phục các lỗi chính tả nhỏ phát sinh trong quá trình sinh chú thích (captioning) tự động cho dữ liệu.

2. Sửa lỗi Kỹ thuật & Hệ thống
* **Lỗi môi trường chạy:** Khắc phục lỗi `OS Error` trong file `quick_test_model.py`, đảm bảo việc kiểm thử nhanh mô hình ổn định.
* **Xử lý giới hạn mô hình:** Giải quyết cảnh báo liên quan đến độ dài chuỗi Token (`Token indices sequence length`) khi dữ liệu đầu vào vượt quá giới hạn cho phép của mô hình.
* **Hạ tầng kết nối:** Sửa lỗi kết nối AnyDesk ("Client Offline - This desk is not available") để đảm bảo việc truy cập điều khiển từ xa thông suốt.

3. Quản lý Kho lưu trữ & Tài liệu
* **Cấu trúc Repo:** Cập nhật tài liệu hướng dẫn về xử lý dữ liệu (data-processing) và điều chỉnh lại cấu trúc repository để dễ quản lý hơn.
* **An toàn mô hình:** Thực hiện các tùy chỉnh liên quan đến bộ lọc an toàn (`safety_checker`) và xử lý các vấn đề liên quan đến nội dung không phù hợp (NSFW) trong giai đoạn đầu.

---
**Ghi chú:** Danh sách này tập trung vào các công việc nền tảng về dữ liệu và hệ thống đã thực hiện trước khi bước vào giai đoạn nước rút làm WebUI và Demo trong vài ngày trở lại đây.
