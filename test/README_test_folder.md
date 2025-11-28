Đây là folder được tạo ra để giải quyết issue #11

Nội dung của folder gồm:
- folder ảnh test: **./images/** lưu ảnh sinh ra từ quá trình nhập caption để test khả năng phản hồi và nhận định các tình huống xảy ra NSFW theo cách thủ công.
 
- folder ảnh dính nsfw: **./nsfw_data**, **./nsfw_data2** tương ứng là 2 folder có chức năng chính là giữ file **metadata.jsonl** chứa các caption thuộc trường hợp bị cảnh báo nsfw.

- file test: **quick_modified_test_model.py** và **quick_nsfw_test_model.py** lần lượt là file kiểm tra data trước và sau khi có giải pháp fix bug. Kết quả kỳ vọng của file **quick_modified_test_model.py** là nhập đầu vào, chạy qua 1 trong 2 mô hình được huấn luyện LoRA từ dữ liệu, nhận kết quả đầu ra là ảnh bình thường hoặc ảnh đen nếu dính NSFW. Kết quả kỳ vọng và thực tế của file **quick_nsfw_test_model.py** là tất cả trường hợp đều trả ra ảnh bình thường.

- file test tự động: **gen_nsfw_filter.py** có chức năng kiểm tra kết quả đầu ra của toàn bộ dữ liệu và lưu lại các caption gặp vấn đề NSFW vào file **metadata.jsonl**

- file phân tích kết quả **metadata.jsonl**: **cluster_nsfw_caption.py** đọc kết quả từ **metadata.jsonl**, thực hiện tokenize, phân cụm vector đầu ra của tokenizer để phân tích sâu hơn về các lý do tạo NSFW. Tuy nhiên, quá trình này đang bị dừng.