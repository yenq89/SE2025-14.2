# Goals and Objectives

### Project Goals

Mục tiêu chính của dự án là thiết kế, triển khai và đánh giá một hệ thống tạo ảnh nghệ thuật dựa trên AI bằng cách fine-tune mô hình mã nguồn mở Stable Diffusion nhằm cải thiện khả năng tạo nhân vật anime mang cảm hứng từ phong cách hình ảnh của Studio Ghibli, so với mô hình SDv1.5 gốc.

Dự án tập trung xây dựng và đánh giá một quy trình hoàn chỉnh (end-to-end pipeline), bao gồm các bước chuẩn bị dữ liệu, fine-tuning mô hình, triển khai inference, xây dựng giao diện web demo và kiểm thử hệ thống.

Bên cạnh đó, dự án hướng tới việc áp dụng các nguyên lý cốt lõi của Công nghệ phần mềm, bao gồm thiết kế hệ thống theo hướng module, kiến trúc API-driven, quản lý phiên bản, theo dõi thí nghiệm và làm việc nhóm minh bạch thông qua GitHub-based workflows.

---

### Project Objectives

Để đạt được các mục tiêu đã đề ra, dự án được triển khai theo các mục tiêu cụ thể sau:

- Thu thập và xây dựng dataset hình ảnh theo phong cách Ghibli từ các khung hình phim hoạt hình, đồng thời thực hiện lọc dữ liệu theo nhiều vòng nhằm nâng cao chất lượng và tính nhất quán của dataset.

- Định nghĩa và áp dụng các tiêu chí đánh giá chất lượng dữ liệu, bao gồm tỷ lệ nhân vật trong khung hình, mức độ đầy đủ của khuôn mặt (mắt, mũi, miệng), góc nhìn nhân vật và bố cục tổng thể.

- Tổ chức nhiều phiên bản dataset khác nhau và phân tích ảnh hưởng của kích thước cũng như chất lượng dataset đến kết quả fine-tuning.

- Thực hiện fine-tuning mô hình Stable Diffusion v1.5 bằng kỹ thuật Low-Rank Adaptation (LoRA), với mục tiêu học đặc trưng phong cách (style) thay vì ghi nhớ các nhân vật cụ thể.

- Tiến hành huấn luyện mô hình với nhiều checkpoint khác nhau và sinh ảnh từ cùng một tập prompt cố định cho từng checkpoint, từ đó thực hiện đánh giá trực quan nhằm lựa chọn checkpoint cho kết quả hình ảnh ổn định và phù hợp phong cách nhất.

- Xây dựng script hỗ trợ batch image generation cho từng checkpoint thuộc từng phiên bản dataset, giúp đảm bảo các điều kiện sinh ảnh nhất quán (prompt, seed, tham số inference) và giảm thao tác thủ công trong quá trình đánh giá bằng mắt.

- Thực hiện kiểm thử giao diện theo các tiêu chí chức năng và độ ổn định, đảm bảo hệ thống sẵn sàng cho demo và đánh giá cuối kỳ.

---

## Scope and Limitations

### Scope

Phạm vi của dự án tập trung vào:
- Phong cách tạo ảnh anime lấy cảm hứng từ Ghibli-style.
- Fine-tuning mô hình Stable Diffusion v1.5 bằng LoRA.
- Đánh giá định tính chất lượng ảnh sinh ra thông qua so sánh trực quan và các tiêu chí thị giác.

Dataset được sử dụng trong dự án phục vụ cho mục đích học tập và nghiên cứu, không nhằm mục đích thương mại.

### Limitations

Dự án tồn tại một số hạn chế như sau:

- Dataset được thu thập từ các khung hình phim hoạt hình có bản quyền, do đó không thể công khai và chỉ được lưu trữ ở chế độ private.

- Việc đánh giá chất lượng ảnh chủ yếu dựa trên đánh giá trực quan (visual evaluation), chưa áp dụng các metric học thuật chuyên sâu.

- Kết quả fine-tuning phụ thuộc nhiều vào chất lượng dataset và số lượng dữ liệu, trong khi số lượng ảnh huấn luyện còn hạn chế so với các mô hình thương mại.

---

## Methodology

Quy trình thực hiện dự án được chia thành các giai đoạn chính sau:

### Dataset Preparation
- Thu thập ảnh từ những bộ phim thuộc Studio Ghibli.
- Sinh caption mô tả nội dung ảnh sử dụng Gemini API.
- Lọc dataset theo các tiêu chí chất lượng (khuôn mặt, bố cục, kích thước nhân vật).
- Tạo nhiều phiên bản dataset để phục vụ huấn luyện và so sánh.

### Model Training
- Sử dụng Stable Diffusion v1.5 làm base model.
- Fine-tune bằng LoRA với các dataset version khác nhau.
- Lưu checkpoint theo các mốc training step.

### Inference
- Thực hiện inference bằng cùng một bộ prompt và tham số cố định.
- Sinh ảnh batch cho từng checkpoint theo từng dataset version.

### Web Demo Interface
- Triển khai backend bằng FastAPI.
- Triển khai frontend bằng HTML/CSS/JavaScript thuần.
- Cho phép load model, sinh ảnh và hiển thị kết quả trực tiếp.

### Testing
- Kiểm thử chức năng load model.
- Kiểm thử sinh ảnh liên tục.
- Kiểm thử xử lý lỗi và độ ổn định hệ thống.

---

## Evaluation and Discussion

### Evaluation Setup

Việc đánh giá được thực hiện bằng cách so sánh trực tiếp ảnh sinh ra từ base model và các model đã fine-tune trong cùng điều kiện sinh ảnh.

**Thông số inference được giữ cố định cho tất cả các model:**
- Prompt #1 <a id="prompt-1"></a>: *Ghibli style, a boy with dark hair and thoughtful eyes, wearing a simple white shirt, looking ahead with a calm expression, outdoors under a bright sky with soft green trees in the background, a gentle, peaceful atmosphere.*
- Seed: cố định
- Steps: 30
- CFG Scale: 7.5
- Resolution: 512 × 512

### Visual Evaluation Criteria

Một ảnh sinh ra được xem là **đạt yêu cầu** nếu thỏa mãn đồng thời các tiêu chí sau:

- Nhân vật chính được thể hiện rõ ràng và đúng chủ thể (con người), không bị lẫn với các đối tượng không liên quan.
- Khuôn mặt nhân vật không bị méo hình hoặc xuất hiện các lỗi nghiêm trọng ảnh hưởng đến khả năng nhận diện (mắt, mũi, miệng bị lệch hoặc biến dạng nặng).
- Tỷ lệ cơ thể và tư thế nhân vật ở mức hợp lý, không xuất hiện các sai lệch hình học rõ rệt.
- Phong cách hình ảnh thể hiện được các đặc trưng chính của Ghibli-style, bao gồm màu sắc dịu, đường nét mềm và cảm giác thị giác mang tính minh họa.

Một ảnh sẽ **không được xem là đạt yêu cầu** nếu xuất hiện một trong các trường hợp sau:

- Xuất hiện đối tượng không mong muốn như động vật hoặc cảnh phong cảnh rộng, làm lệch trọng tâm đánh giá phong cách nhân vật.
- Xuất hiện các artefact nặng thường gặp trong mô hình diffusion, chẳng hạn như tay thừa, khuôn mặt bị vỡ cấu trúc hoặc hiện tượng blur mạnh làm giảm chất lượng ảnh.

---

### Model Comparison
| Prompt | Model | Ảnh sinh ra |
|--------|-------|------------|
| [#1](#prompt-1) | SD v1.5 (Base) | ![](test\images\SE14.2_ouput_test_demo\v0.png) |
| [#1](#prompt-1) | LoRA Ghibli v1 | ![](test\images\SE14.2_ouput_test_demo\v1.png) |
| [#1](#prompt-1) | LoRA Ghibli v2 | ![](test\images\SE14.2_ouput_test_demo\v2.png) |
| [#1](#prompt-1) | LoRA Ghibli v3 | ![](test\images\SE14.2_ouput_test_demo\v3.png) |
| [#1](#prompt-1) | LoRA Ghibli v4 | ![](test\images\SE14.2_ouput_test_demo\v4.1.png) |
| [#1](#prompt-1) | LoRA Ghibli v5 | ![](test\images\SE14.2_ouput_test_demo\v5.png) |

> **Lưu ý:** Tất cả ảnh trong bảng được sinh ra với cùng prompt, seed và tham số inference để đảm bảo tính công bằng khi so sánh.

### Discussion

Qua so sánh, có thể quan sát thấy rằng các model fine-tuned bằng LoRA thể hiện phong cách Ghibli rõ rệt hơn so với base model. Đặc biệt, các dataset đã được lọc kỹ cho kết quả ổn định và nhất quán hơn, trong khi dataset lớn nhưng chưa được lọc kỹ có xu hướng tạo ảnh nhiễu phong cách.

Một số checkpoint cho thấy dấu hiệu overfitting, thể hiện qua việc giảm đa dạng hình ảnh dù phong cách rõ hơn. Điều này cho thấy chất lượng dataset đóng vai trò quan trọng hơn số lượng dữ liệu trong bài toán fine-tuning theo phong cách.

---

## Conclusion and Future Work

### Conclusion

Dự án đã xây dựng thành công một pipeline hoàn chỉnh cho bài toán tạo ảnh nghệ thuật theo phong cách anime bằng Stable Diffusion. Từ khâu chuẩn bị dữ liệu, fine-tuning mô hình, triển khai inference đến xây dựng web demo và kiểm thử hệ thống, các mục tiêu đề ra đều đã được thực hiện.

Kết quả cho thấy việc fine-tune Stable Diffusion bằng LoRA có thể cải thiện đáng kể khả năng tái tạo phong cách hình ảnh khi dataset được chuẩn bị cẩn thận.

### Future Work

Trong tương lai, dự án có thể được mở rộng theo các hướng:
- Tiếp tục điều chỉnh và tối ưu các tham số huấn luyện trong quá trình fine-tuning, bao gồm learning rate, số bước training, batch size và cấu hình LoRA, nhằm cải thiện tính ổn định và mức độ nhất quán của phong cách sinh ảnh.
- Tập trung nâng cao chất lượng dataset, đặc biệt là việc lựa chọn và lọc dữ liệu đầu vào, do chất lượng dữ liệu được nhận định là yếu tố có ảnh hưởng lớn hơn số lượng dữ liệu trong bài toán fine-tuning theo phong cách.
- Khảo sát và áp dụng thêm các phương pháp đánh giá định lượng nhẹ, chẳng hạn như CLIP similarity, để bổ trợ cho đánh giá trực quan và giảm tính chủ quan trong quá trình lựa chọn checkpoint.
- Triển khai hệ thống dưới dạng dịch vụ web hoàn chỉnh với khả năng mở rộng.
