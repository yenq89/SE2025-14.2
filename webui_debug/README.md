# Mục đích: 
**Folder webui_debug** được tạo ra nhằm phục vụ mục tiêu kiểm tra và giải quyết ván đề từ issue `#5`. Cụ thể, giao diện WebUI gặp vấn đề, khiến việc *test* các mô hình LoRA hoặc mô hình đầy đủ sau *train* là không thể, và trả ra kết quả ảnh xám không có nội dung.

# Cấu trúc thư mục (debug lần 1):
- File mô tả cấu trúc thư mục: `./webui_debug/README.md`
- File đọc keys của mô hình: `./webui_debug/inspect_lora_keys.py`, có chức năng đọc file có đuôi `.safetensors` để lấy ra cấu trúc key bên trong mô hình *(SD 1.5, LoRA, hoặc đầy đủ)*.
- File đầu ra sau khi đọc key: 
  - `./webui_debug/lora_keys_list_origin.txt` (SD 1.5); 
  - `./webui_debug/lora_keys_list_ver1_FULL.txt` và `./webui_debug/lora_keys_list_ver4.txt` (mô hình đầy đủ); 
  - `./webui_debug/lora_keys_list_ver1_LoRA.txt` (LoRA).


# Cấu trúc thư mục bổ sung (debug lần 2):
- File đọc cấu trúc thư mục `stable-diffusion-webui`: `list_all_files.py`, phục vụ debug lần 2