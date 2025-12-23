# Goals and Objectives

### Project Goals

Mục tiêu chính của dự án là thiết kế, triển khai và đánh giá một hệ thống tạo ảnh nghệ thuật dựa trên AI bằng cách fine-tune mô hình mã nguồn mở Stable Diffusion, tập trung vào khả năng tạo nhân vật anime mang cảm hứng từ phong cách hình ảnh của Studio Ghibli, dựa trên mô hình SDv1.5 gốc.

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

- Tổng hợp kết quả, bao gồm biểu đồ loss, ảnh validation thu được khi train, và ảnh sinh dựa theo prompt test, sau đó phân tích và đánh giá hiệu quả của mô hình.

- Thực hiện kiểm thử giao diện theo các tiêu chí chức năng và độ ổn định, đảm bảo hệ thống sẵn sàng cho demo và đánh giá cuối kỳ.

---

## Scope and Limitations

### Scope

Phạm vi của dự án tập trung vào:
- Phong cách tạo ảnh anime lấy cảm hứng từ Ghibli-style.
- Fine-tuning mô hình Stable Diffusion v1.5 bằng LoRA.
- Đánh giá định tính chất lượng ảnh sinh ra thông qua so sánh trực quan và các tiêu chí thị giác.
- Đánh giá định lượng khả năng học của mô hình bằng **Noise Prediction Loss**.

Dataset bao gồm ảnh từ các bộ phim Ghibli sau:

1. **Arrietty** 
2. **From Up on Poppy Hill** 
3. **Grave of the Fireflies** 
4. **Howl's Moving Castle** 
5. **Kiki's Delivery Service**
6. **Whisper of the Heart** 
7. **Spirited Away**
8. **The Wind Rises**
9. **Ponyo**

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
- Fine-tune bằng LoRA với các dataset version khác nhau, và nhiều bộ tham số khác nhau cho mỗi dataset version.
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

## Dataset Construction and Versioning

Trong quá trình thực hiện dự án, nhóm đã xây dựng và sử dụng nhiều phiên bản dataset khác nhau nhằm phân tích ảnh hưởng của nguồn dữ liệu, chất lượng dữ liệu và chiến lược lọc dữ liệu đến kết quả fine-tuning mô hình. Mỗi phiên bản dataset phản ánh một giai đoạn thử nghiệm và điều chỉnh khác nhau trong quá trình phát triển.

### Dataset Version 1 (v1)

Dataset v1 được thu thập bằng cách crawl ảnh từ các nguồn web công khai sử dụng thư viện `simple_image_download` trong Python.  
Bộ dữ liệu này bao gồm **171 ảnh**, chủ yếu là hình minh họa anime theo từ khóa liên quan đến Ghibli-style.

Tuy nhiên, do phụ thuộc vào kết quả tìm kiếm trên web, dataset v1 có số lượng ảnh hạn chế và chất lượng không đồng đều, dẫn đến kết quả huấn luyện chưa ổn định.


### Dataset Version 2 (v2)

Dataset v2 tiếp tục sử dụng phương pháp crawl ảnh tự động bằng `simple_image_download`, với việc mở rộng từ khóa tìm kiếm.  
Phiên bản này thu thập được **292 ảnh**, tăng nhẹ về số lượng so với v1.

Mặc dù số lượng ảnh tăng lên, chất lượng dữ liệu vẫn chưa được cải thiện đáng kể do:
- Nguồn ảnh bị giới hạn
- Phong cách hình ảnh không nhất quán
- Một số ảnh không phù hợp hoàn toàn với mục tiêu học phong cách nhân vật


### Dataset Version 3 (v3)

Sau khi nhận thấy chất lượng huấn luyện từ các dataset crawl web không đạt yêu cầu, nhóm quyết định **thay đổi chiến lược thu thập dữ liệu**.

Ở phiên bản v3, dataset được xây dựng bằng cách **xem phim hoạt hình và tự động crop các khung hình** để trích xuất ảnh huấn luyện.  
Cách tiếp cận này giúp:
- Chủ động kiểm soát nội dung hình ảnh
- Đảm bảo phong cách hình ảnh nhất quán hơn

Dataset v3 thu thập được **4,776 ảnh**, tuy nhiên bộ dữ liệu này vẫn còn chứa:
- Nhiều ảnh có **nhiều nhân vật trong cùng một khung hình**
- Một số ảnh có **động vật**
- Một số ảnh có bố cục phức tạp hoặc nhân vật quá nhỏ trong khung hình

Phiên bản này đóng vai trò là dataset lớn nhưng chưa được lọc kỹ.


### Dataset Version 4 (v4)

Dataset v4 được tạo ra bằng cách **lọc lại dataset v3** nhằm nâng cao chất lượng dữ liệu đầu vào.  
Các tiêu chí lọc chính bao gồm:
- Loại bỏ ảnh có động vật
- Loại bỏ ảnh có nhiều nhân vật
- Loại bỏ các góc chụp không rõ mặt hoặc bố cục không phù hợp

Sau khi lọc, dataset v4 còn lại **290 ảnh**, tập trung vào các ảnh có một nhân vật người với bố cục và khuôn mặt rõ ràng hơn.

Phiên bản này thể hiện sự đánh đổi rõ rệt giữa **số lượng và chất lượng dữ liệu**.


### Dataset Version 5 (v5)

Dataset v5 tiếp tục được lọc từ dataset v4 với tiêu chí nghiêm ngặt hơn, chỉ giữ lại các ảnh:
- Khuôn mặt nhân vật rõ ràng, không lỗi
- Bố cục đơn giản, nhân vật là trung tâm khung hình

Kết quả, dataset v5 chỉ còn **28 ảnh**, đại diện cho tập dữ liệu nhỏ nhất nhưng có chất lượng được đánh giá tốt hơn version 1, 2, 3.

Phiên bản này được sử dụng để khảo sát ảnh hưởng của dataset cực nhỏ nhưng được lọc kỹ đến kết quả fine-tuning theo phong cách.


### Summary of Dataset Versions

| Dataset Version | Số lượng ảnh | Phương pháp thu thập | Đặc điểm chính |
|-----------------|-------------|----------------------|----------------|
| v1 | 171 | Crawl web + (`simple_image_download`) lib | Nhỏ, chất lượng không đồng đều |
| v2 | 292 | Crawl web + (`simple_image_download`) lib | Số lượng tăng, style chưa ổn định |
| v3 | 4,776 | Crop từ phim hoạt hình | Lớn, chưa lọc kỹ |
| v4 | 290 | Lọc từ v3 | Chất lượng cao, tập trung nhân vật |
| v5 | 28 | Lọc từ v4 | Rất nhỏ |

Phần đánh giá tiếp theo sẽ phân tích ảnh hưởng của các phiên bản dataset này đến kết quả sinh ảnh của mô hình trong cùng điều kiện inference.

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
| [#1](#prompt-1) | SD v1.5 (Base) | ![](https://github.com/yenq89/SE2025-14.2/blob/79f65c95ea8dac6d7fa9ed56c2b81e553e1d26d5/test/images/SE14.2_ouput_test_demo/v0.png) |
| [#1](#prompt-1) | LoRA Ghibli v1 | ![](https://github.com/yenq89/SE2025-14.2/blob/79f65c95ea8dac6d7fa9ed56c2b81e553e1d26d5/test/images/SE14.2_ouput_test_demo/v1.png) |
| [#1](#prompt-1) | LoRA Ghibli v2 | ![](https://github.com/yenq89/SE2025-14.2/blob/79f65c95ea8dac6d7fa9ed56c2b81e553e1d26d5/test/images/SE14.2_ouput_test_demo/v2.png) |
| [#1](#prompt-1) | LoRA Ghibli v3 | ![](https://github.com/yenq89/SE2025-14.2/blob/79f65c95ea8dac6d7fa9ed56c2b81e553e1d26d5/test/images/SE14.2_ouput_test_demo/v3.png) |
| [#1](#prompt-1) | LoRA Ghibli v4 | ![](https://github.com/yenq89/SE2025-14.2/blob/79f65c95ea8dac6d7fa9ed56c2b81e553e1d26d5/test/images/SE14.2_ouput_test_demo/v4.1.png) |
| [#1](#prompt-1) | LoRA Ghibli v5 | ![](https://github.com/yenq89/SE2025-14.2/blob/79f65c95ea8dac6d7fa9ed56c2b81e553e1d26d5/test/images/SE14.2_ouput_test_demo/v5.png) |

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
