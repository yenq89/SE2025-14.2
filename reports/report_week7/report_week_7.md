# Báo cáo công việc tuần 7 - Dự án LoRA Ghibli SD

## Mục tiêu tuần:
- Huấn luyện LoRA
- Đánh giá hiệu quả mô hình thông qua hàm loss và ảnh sinh được.
- Tìm ra bộ tham số phù hợp.
- Tìm ra mô hình tốt nhất và bộ dữ liệu tương ứng.

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

### 
