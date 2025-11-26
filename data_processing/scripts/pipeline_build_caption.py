"""
Pipeline Chuẩn Bị Dữ Liệu Huấn Luyện LoRA Phong Cách Ghibli
============================================================

Quy trình:
1. Lọc ảnh có người & đặt tên lại (1.jpg, 2.jpg, ...)
2. Resize về 512x512 pixels
3. Gen caption với Gemini API (hỗ trợ nhiều keys + checkpoint)
4. Lưu vào data/ghibli/train/
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import google.generativeai as genai
from tqdm import tqdm
import time
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


# ==================== CẤU HÌNH ====================

class Config:
    """Cấu hình pipeline"""
    
    # Đường dẫn
    SOURCE_DIR = r"d:\SE_Data\ghibli_data"
    OUTPUT_DIR = r"d:\SE_Data\data\ghibli\train"
    CHECKPOINT_FILE = r"d:\SE_Data\checkpoint.json"
    
    # Kích thước ảnh
    TARGET_SIZE = (512, 512)
    
    # Gemini API
    GEMINI_API_KEYS = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3"),
        os.getenv("GEMINI_API_KEY_4"),
        os.getenv("GEMINI_API_KEY_5"),
    ]
    
    # Model Failover Strategy - Thứ tự ưu tiên cho mỗi API key
    MODEL_PRIORITY = [
        "gemini-2.5-flash",           # A.1: Chất lượng cao, tốc độ tốt
        "gemini-2.5-flash-lite",      # A.2: RPD cao hơn
        "gemini-2.0-flash",           # A.3: TPM cao hơn
        "gemini-2.0-flash-lite",      # A.4: RPM cao nhất
    ]
    
    # Prompt cho caption
    CAPTION_PROMPT = """
You will receive an image. Describe it in a detailed Ghibli-style caption.
Rules:

Structure: Write the caption as a single descriptive phrase using commas for separation (do not use full stops/periods).
Start with: "Ghibli style". (No colon or commas needed after the starter).
Language Level: Use A2-B1 simple vocabulary and grammar.
Content: Describe age, gender, expression, and clothing. Describe posture or action. Describe the background environment with simple details (light, mood, atmosphere).
Exclusions: Do NOT include any character names, even if recognizable. Never mention Studio Ghibli character names or movie titles.
Length: Make the caption at least 20-30 words (since the structure is limited to one simple sentence).
"""

    # Retry settings for Rate Limit (429)
    MAX_RETRIES_RATE_LIMIT = 5
    INITIAL_BACKOFF = 5  # seconds - Exponential backoff starting point
    MAX_BACKOFF = 64  # seconds - Maximum backoff time


# ==================== BƯỚC 1: LỌC ẢNH CÓ NGƯỜI ====================

class PersonDetector:
    """Phát hiện ảnh có người sử dụng MediaPipe hoặc YOLO"""
    
    def __init__(self):
        self.detector = None
        self._init_detector()
    
    def _init_detector(self):
        """Khởi tạo detector"""
        try:
            # Thử sử dụng MediaPipe trước
            import mediapipe as mp
            self.detector = mp.solutions.pose.Pose(
                static_image_mode=True,
                min_detection_confidence=0.5
            )
            self.detector_type = "mediapipe"
            print("✓ Sử dụng MediaPipe để phát hiện người")
        except ImportError:
            try:
                # Fallback sang YOLOv8
                from ultralytics import YOLO
                self.detector = YOLO('yolov8n.pt')
                self.detector_type = "yolo"
                print("✓ Sử dụng YOLOv8 để phát hiện người")
            except ImportError:
                print("⚠ Không tìm thấy thư viện phát hiện người. Bỏ qua bước lọc.")
                self.detector_type = "none"
    
    def has_person(self, image_path: str) -> bool:
        """Kiểm tra ảnh có người hay không"""
        if self.detector_type == "none":
            return True  # Skip filtering nếu không có detector
        
        try:
            if self.detector_type == "mediapipe":
                import cv2
                image = cv2.imread(image_path)
                results = self.detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                return results.pose_landmarks is not None
            
            elif self.detector_type == "yolo":
                results = self.detector(image_path, verbose=False)
                # Class 0 là 'person' trong COCO dataset
                for r in results:
                    if 0 in r.boxes.cls:
                        return True
                return False
        except Exception as e:
            print(f"⚠ Lỗi khi kiểm tra {image_path}: {e}")
            return True  # Giữ ảnh nếu có lỗi


# ==================== BƯỚC 2 & 3: XỬ LÝ ẢNH ====================

def resize_image(image_path: str, output_path: str, size: tuple = (512, 512)):
    """
    Resize ảnh về kích thước mục tiêu (997x997 -> 512x512)
    
    Lưu ý: Ảnh gốc đã là 997×997 (square frame từ auto capture tool),
    nên chỉ cần resize trực tiếp mà không cần center crop.
    
    Args:
        image_path: Đường dẫn ảnh gốc (997×997)
        output_path: Đường dẫn lưu ảnh đã resize (512×512)
        size: Kích thước mục tiêu (width, height)
    """
    try:
        img = Image.open(image_path)
        
        # Convert sang RGB nếu cần
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize trực tiếp với LANCZOS (chất lượng cao)
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Lưu
        img.save(output_path, 'JPEG', quality=95)
        return True
        
    except Exception as e:
        print(f"⚠ Lỗi resize {image_path}: {e}")
        return False


# ==================== BƯỚC 4: GEN CAPTION ====================

class GeminiCaptioner:
    """
    Tạo caption với Gemini API - Model Failover Strategy
    
    Chiến lược:
    1. Rate Limit (429) → Exponential Backoff
    2. Quota Exceeded (RPD/TPD) → Chuyển model tiếp theo
    3. Hết models trong key → Chuyển API key tiếp theo
    """
    
    def __init__(self, api_keys: List[str], checkpoint_file: str):
        self.api_keys = [key for key in api_keys if key]  # Lọc keys rỗng
        self.current_key_index = 0
        self.current_model_index = 0
        self.checkpoint_file = checkpoint_file
        self.model = None
        
        if not self.api_keys:
            raise ValueError("Không tìm thấy API key nào! Vui lòng cấu hình GEMINI_API_KEY trong .env")
        
        self._init_model()
    
    def _init_model(self):
        """Khởi tạo model với key và model hiện tại"""
        genai.configure(api_key=self.api_keys[self.current_key_index])
        model_name = Config.MODEL_PRIORITY[self.current_model_index]
        self.model = genai.GenerativeModel(model_name)
        
        print(f"✓ Sử dụng API Key #{self.current_key_index + 1}/{len(self.api_keys)} | "
              f"Model: {model_name} ({self.current_model_index + 1}/{len(Config.MODEL_PRIORITY)})")
    
    def _switch_to_next_model(self) -> bool:
        """Chuyển sang model tiếp theo trong cùng API key"""
        self.current_model_index += 1
        
        if self.current_model_index >= len(Config.MODEL_PRIORITY):
            # Hết models, chuyển sang key tiếp theo
            return self._switch_to_next_key()
        
        model_name = Config.MODEL_PRIORITY[self.current_model_index]
        print(f"⟳ Chuyển sang model: {model_name} (ưu tiên #{self.current_model_index + 1})")
        self._init_model()
        return True
    
    def _switch_to_next_key(self) -> bool:
        """Chuyển sang API key tiếp theo và reset model index"""
        self.current_key_index += 1
        
        if self.current_key_index >= len(self.api_keys):
            return False  # Hết tất cả keys
        
        # Reset về model đầu tiên khi chuyển key
        self.current_model_index = 0
        print(f"\n⟳ Chuyển sang API Key #{self.current_key_index + 1}/{len(self.api_keys)}")
        self._init_model()
        return True
    
    def _exponential_backoff(self, attempt: int) -> float:
        """
        Tính thời gian chờ theo Exponential Backoff
        
        Args:
            attempt: Số lần thử (0-indexed)
            
        Returns:
            Thời gian chờ (giây)
        """
        backoff = min(Config.INITIAL_BACKOFF * (2 ** attempt), Config.MAX_BACKOFF)
        return backoff
    
    def generate_caption(self, image_path: str) -> Optional[str]:
        """
        Tạo caption cho ảnh với Model Failover Strategy
        
        Args:
            image_path: Đường dẫn đến ảnh
            
        Returns:
            Caption string hoặc None nếu thất bại
        """
        for attempt in range(Config.MAX_RETRIES_RATE_LIMIT):
            try:
                # Upload ảnh
                img = Image.open(image_path)
                
                # Tạo caption
                response = self.model.generate_content([
                    Config.CAPTION_PROMPT,
                    img
                ])
                
                return response.text.strip()
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # ========== XỬ LÝ BLOCKED PROMPT (Safety Filter) ==========
                if "block_reason" in error_msg or "blocked" in error_msg or "candidates` is empty" in error_msg:
                    print(f"⚠ Ảnh bị chặn bởi safety filter (có thể chứa nội dung nhạy cảm): {os.path.basename(image_path)}")
                    return "[BLOCKED_BY_SAFETY_FILTER]"  # Đánh dấu để bỏ qua
                
                # ========== XỬ LÝ RATE LIMIT (429) ==========
                elif "429" in error_msg or "rate" in error_msg or "too many requests" in error_msg:
                    if attempt < Config.MAX_RETRIES_RATE_LIMIT - 1:
                        backoff_time = self._exponential_backoff(attempt)
                        print(f"⏳ Rate Limit! Chờ {backoff_time:.1f}s trước khi thử lại... "
                              f"(lần {attempt + 1}/{Config.MAX_RETRIES_RATE_LIMIT})")
                        time.sleep(backoff_time)
                        continue
                    else:
                        print(f"⚠ Vẫn bị Rate Limit sau {Config.MAX_RETRIES_RATE_LIMIT} lần thử")
                        # Chuyển model nếu backoff không giải quyết được
                        if self._switch_to_next_model():
                            return self.generate_caption(image_path)  # Thử lại với model mới
                        else:
                            return None
                
                # ========== XỬ LÝ HẾT QUOTA (RPD/TPD) ==========
                elif "quota" in error_msg or "resource_exhausted" in error_msg or "limit exceeded" in error_msg:
                    print(f"⚠ Model hiện tại đã hết quota (RPD/TPD)")
                    
                    if self._switch_to_next_model():
                        # Thử lại ngay với model/key mới
                        return self.generate_caption(image_path)
                    else:
                        print("✗ Đã hết tất cả API keys và models!")
                        return None
                
                # ========== CÁC LỖI KHÁC (CÓ THỂ RETRY) ==========
                else:
                    if attempt < Config.MAX_RETRIES_RATE_LIMIT - 1:
                        print(f"⚠ Lỗi: {e} (thử lại {attempt + 1}/{Config.MAX_RETRIES_RATE_LIMIT})")
                        time.sleep(5)  # Chờ 5 giây trước khi thử lại
                        continue
                    else:
                        print(f"✗ Không thể tạo caption cho {image_path}: {e}")
                        return None
        
        return None
    
    def save_checkpoint(self, data: Dict):
        """Lưu checkpoint bao gồm cả trạng thái model & key"""
        checkpoint_data = {
            **data,
            'current_key_index': self.current_key_index,
            'current_model_index': self.current_model_index,
            'current_model': Config.MODEL_PRIORITY[self.current_model_index]
        }
        
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
    
    def load_checkpoint(self) -> Optional[Dict]:
        """Đọc checkpoint và khôi phục trạng thái model & key"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                
                # Khôi phục trạng thái model & key
                if 'current_key_index' in checkpoint:
                    self.current_key_index = checkpoint['current_key_index']
                if 'current_model_index' in checkpoint:
                    self.current_model_index = checkpoint['current_model_index']
                    self._init_model()  # Khởi tạo lại model đúng
                
                return checkpoint
            except Exception as e:
                print(f"⚠ Không đọc được checkpoint: {e}")
        return None


# ==================== PIPELINE CHÍNH ====================

class GhibliDataPipeline:
    """Pipeline chính để xử lý dữ liệu"""
    
    def __init__(self):
        self.config = Config()
        self.person_detector = PersonDetector()
        self.captioner = None
        
        # Tạo thư mục output
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
    
    def step1_filter_and_rename(self) -> Dict[str, List[str]]:
        """
        Bước 1: Lọc ảnh có người và tổ chức lại
        
        Returns:
            Dict mapping folder_name -> list of filtered image paths
        """
        print("\n" + "="*60)
        print("BƯỚC 1: LỌC ẢNH VÀ ĐẶT TÊN LẠI")
        print("="*60)
        
        filtered_images = {}
        
        # Duyệt qua từng thư mục phim
        movie_folders = [f for f in os.listdir(self.config.SOURCE_DIR) 
                        if os.path.isdir(os.path.join(self.config.SOURCE_DIR, f))]
        
        for folder in sorted(movie_folders):
            folder_path = os.path.join(self.config.SOURCE_DIR, folder)
            print(f"\n📁 Xử lý: {folder}")
            
            # Lấy danh sách ảnh
            image_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            # Lọc ảnh có người
            valid_images = []
            for img_file in tqdm(image_files, desc=f"  Lọc {folder}"):
                img_path = os.path.join(folder_path, img_file)
                if self.person_detector.has_person(img_path):
                    valid_images.append(img_path)
            
            filtered_images[folder] = valid_images
            print(f"  ✓ Giữ lại {len(valid_images)}/{len(image_files)} ảnh")
        
        return filtered_images
    
    def step2_resize_images(self, filtered_images: Dict[str, List[str]]) -> List[str]:
        """
        Bước 2: Resize ảnh và lưu với tên mới
        
        Args:
            filtered_images: Dict từ bước 1
            
        Returns:
            List các đường dẫn ảnh đã resize
        """
        print("\n" + "="*60)
        print("BƯỚC 2: RESIZE ẢNH VỀ 512x512")
        print("="*60)
        
        resized_images = []
        counter = 1
        
        for folder, image_paths in filtered_images.items():
            print(f"\n📁 Resize: {folder}")
            
            for img_path in tqdm(image_paths, desc=f"  Resize {folder}"):
                output_filename = f"{counter}.jpg"
                output_path = os.path.join(self.config.OUTPUT_DIR, output_filename)
                
                if resize_image(img_path, output_path, self.config.TARGET_SIZE):
                    resized_images.append(output_path)
                    counter += 1
        
        print(f"\n✓ Đã resize {len(resized_images)} ảnh")
        return resized_images
    
    def step3_generate_captions(self, image_paths: List[str]):
        """
        Bước 3: Tạo caption cho ảnh
        
        Args:
            image_paths: Danh sách đường dẫn ảnh đã resize
        """
        print("\n" + "="*60)
        print("BƯỚC 3: TẠO CAPTION VỚI GEMINI API")
        print("="*60)
        
        # Khởi tạo captioner
        self.captioner = GeminiCaptioner(
            self.config.GEMINI_API_KEYS,
            self.config.CHECKPOINT_FILE
        )
        
        # Đường dẫn file metadata
        metadata_path = os.path.join(self.config.OUTPUT_DIR, "metadata.jsonl")
        
        # Đọc metadata hiện có để tìm ảnh đã xử lý
        processed_files = set()
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            processed_files.add(entry.get('file_name'))
                print(f"⟳ Đã tìm thấy {len(processed_files)} ảnh đã có caption")
            except Exception as e:
                print(f"⚠ Không đọc được metadata: {e}")
        
        # Kiểm tra checkpoint
        checkpoint = self.captioner.load_checkpoint()
        start_index = 0
        
        if checkpoint and checkpoint.get('last_processed'):
            start_index = checkpoint['last_processed'] + 1
            print(f"⟳ Checkpoint: tiếp tục từ index #{start_index}")
        
        # Tạo caption
        with open(metadata_path, 'a', encoding='utf-8') as f:
            for idx in tqdm(range(start_index, len(image_paths)), 
                           desc="  Tạo caption", 
                           initial=start_index, 
                           total=len(image_paths)):
                
                img_path = image_paths[idx]
                filename = os.path.basename(img_path)
                
                # Bỏ qua nếu đã xử lý rồi
                if filename in processed_files:
                    continue
                
                # Gen caption
                caption = self.captioner.generate_caption(img_path)
                
                if caption == "[BLOCKED_BY_SAFETY_FILTER]":
                    # Ảnh bị block - ghi vào log và bỏ qua
                    print(f"\n⊘ Bỏ qua {filename} (bị chặn bởi safety filter)")
                    # Vẫn lưu checkpoint để không xử lý lại ảnh này
                    self.captioner.save_checkpoint({
                        'last_processed': idx,
                        'total_images': len(image_paths),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    continue
                
                if caption:
                    # Lưu vào metadata.jsonl
                    metadata_entry = {
                        "file_name": filename,
                        "text": caption
                    }
                    f.write(json.dumps(metadata_entry, ensure_ascii=False) + '\n')
                    f.flush()  # Đảm bảo ghi ngay
                    
                    # Thêm vào processed_files
                    processed_files.add(filename)
                    
                    # Lưu checkpoint
                    self.captioner.save_checkpoint({
                        'last_processed': idx,
                        'total_images': len(image_paths),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    print(f"\n✗ Không thể tạo caption cho {filename}")
                    # Dừng lại nếu không tạo được caption (lỗi nghiêm trọng)
                    print("⚠ Dừng pipeline. Vui lòng kiểm tra API keys và chạy lại.")
                    return
        
        print(f"\n✓ Hoàn thành tạo caption cho {len(image_paths)} ảnh")
        print(f"✓ Metadata đã lưu tại: {metadata_path}")
        
        # Xóa checkpoint sau khi hoàn thành
        if os.path.exists(self.config.CHECKPOINT_FILE):
            os.remove(self.config.CHECKPOINT_FILE)
    
    def run(self, skip_filter: bool = False, skip_resize: bool = False):
        """
        Chạy toàn bộ pipeline
        
        Args:
            skip_filter: Bỏ qua bước lọc ảnh (dùng khi đã lọc rồi)
            skip_resize: Bỏ qua bước resize (dùng khi đã resize rồi)
        """
        print("\n" + "="*60)
        print("PIPELINE CHUẨN BỊ DỮ LIỆU GHIBLI LORA")
        print("="*60)
        
        if skip_filter and skip_resize:
            # Chỉ chạy gen caption
            print("\n⏭ Bỏ qua bước lọc và resize")
            image_paths = sorted([
                os.path.join(self.config.OUTPUT_DIR, f)
                for f in os.listdir(self.config.OUTPUT_DIR)
                if f.lower().endswith(('.jpg', '.jpeg'))
            ], key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            
            self.step3_generate_captions(image_paths)
        else:
            # Chạy full pipeline
            if not skip_filter:
                filtered_images = self.step1_filter_and_rename()
            else:
                print("\n⏭ Bỏ qua bước lọc - Load tất cả ảnh từ SOURCE_DIR")
                # Load tất cả ảnh từ thư mục gốc
                filtered_images = {}
                movie_folders = [f for f in os.listdir(self.config.SOURCE_DIR) 
                                if os.path.isdir(os.path.join(self.config.SOURCE_DIR, f))]
                
                for folder in sorted(movie_folders):
                    folder_path = os.path.join(self.config.SOURCE_DIR, folder)
                    image_files = [
                        os.path.join(folder_path, f) 
                        for f in os.listdir(folder_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                    ]
                    filtered_images[folder] = image_files
                    print(f"  📁 {folder}: {len(image_files)} ảnh")
            
            if not skip_resize:
                resized_images = self.step2_resize_images(filtered_images)
            else:
                print("\n⏭ Bỏ qua bước resize")
                # Load existing images
                resized_images = sorted([
                    os.path.join(self.config.OUTPUT_DIR, f)
                    for f in os.listdir(self.config.OUTPUT_DIR)
                    if f.lower().endswith(('.jpg', '.jpeg'))
                ], key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            
            self.step3_generate_captions(resized_images)
        
        print("\n" + "="*60)
        print("✓ HOÀN THÀNH PIPELINE!")
        print("="*60)
        print(f"\nDữ liệu đã lưu tại: {self.config.OUTPUT_DIR}")


# ==================== MAIN ====================

if __name__ == "__main__":
    # Tạo pipeline
    pipeline = GhibliDataPipeline()
    
    # Chạy pipeline
    # Tùy chỉnh tham số nếu cần:
    # - skip_filter=True: Bỏ qua bước lọc ảnh
    # - skip_resize=True: Bỏ qua bước resize (chỉ chạy gen caption)
    
    # pipeline.run()
    
    # Bỏ qua lọc ảnh, nhưng vẫn resize và gen caption:
    # pipeline.run(skip_filter=True, skip_resize=False)
    
    # Hoặc chỉ chạy gen caption nếu đã có ảnh:
    pipeline.run(skip_filter=True, skip_resize=True)
