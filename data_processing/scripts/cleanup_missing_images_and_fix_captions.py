"""
Script tự động dọn dẹp và chuẩn hóa dataset:
1. Xóa ảnh không có caption trong metadata.jsonl
2. Đổi tên ảnh còn lại theo thứ tự 1.jpg, 2.jpg, ...
3. Cập nhật file_name trong metadata.jsonl
4. Loại bỏ dấu phẩy sau "Ghibli style" trong caption
"""

import json
import os
import shutil
from pathlib import Path

# Cấu hình
IMAGE_DIR = Path(r"d:\SE_Data\data\ghibli\train")
METADATA_FILE = IMAGE_DIR / "metadata.jsonl"
BACKUP_DIR = Path(r"d:\SE_Data\backups")

def backup_files():
    """Sao lưu metadata và folder ảnh trước khi xử lý"""
    print("\n" + "="*80)
    print("SAO LƯU DỮ LIỆU")
    print("="*80)
    
    # Tạo thư mục backup với timestamp
    import time
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Backup metadata
    if METADATA_FILE.exists():
        shutil.copy2(METADATA_FILE, backup_path / "metadata.jsonl")
        print(f"✓ Đã backup metadata.jsonl")
    
    # Backup toàn bộ folder ảnh
    backup_images_dir = backup_path / "images"
    backup_images_dir.mkdir(exist_ok=True)
    
    image_count = 0
    for img_file in IMAGE_DIR.glob("*.jpg"):
        shutil.copy2(img_file, backup_images_dir / img_file.name)
        image_count += 1
    
    print(f"✓ Đã backup {image_count} ảnh")
    print(f"✓ Backup lưu tại: {backup_path}")
    
    return backup_path

def load_metadata():
    """Đọc metadata.jsonl và trả về list các entries"""
    entries = []
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError as e:
                        print(f"⚠ Lỗi parse JSON: {e}")
    return entries

def get_existing_images():
    """Lấy danh sách tất cả file ảnh .jpg trong thư mục"""
    return sorted([f.name for f in IMAGE_DIR.glob("*.jpg")], 
                  key=lambda x: int(x.replace('.jpg', '')))

def step1_remove_images_without_caption():
    """
    Bước 1: Xóa ảnh không có trong metadata.jsonl
    Returns: set of file_names có caption
    """
    print("\n" + "="*80)
    print("BƯỚC 1: XÓA ẢNH KHÔNG CÓ CAPTION")
    print("="*80)
    
    # Lấy danh sách file_name có caption
    metadata_entries = load_metadata()
    captioned_files = {entry['file_name'] for entry in metadata_entries}
    
    print(f"\nSố caption trong metadata: {len(captioned_files)}")
    
    # Lấy danh sách ảnh hiện có
    existing_images = get_existing_images()
    print(f"Số ảnh trong folder: {len(existing_images)}")
    
    # Tìm ảnh cần xóa
    images_to_delete = []
    for img_file in existing_images:
        if img_file not in captioned_files:
            images_to_delete.append(img_file)
    
    if not images_to_delete:
        print("\n✓ Không có ảnh nào cần xóa")
        return captioned_files
    
    print(f"\n⚠ Tìm thấy {len(images_to_delete)} ảnh không có caption:")
    for img in images_to_delete[:10]:  # Hiển thị tối đa 10 ảnh
        print(f"  - {img}")
    if len(images_to_delete) > 10:
        print(f"  ... và {len(images_to_delete) - 10} ảnh khác")
    
    # Xóa ảnh
    for img_file in images_to_delete:
        img_path = IMAGE_DIR / img_file
        if img_path.exists():
            img_path.unlink()
    
    print(f"\n✓ Đã xóa {len(images_to_delete)} ảnh")
    
    return captioned_files

def step2_rename_images_sequentially(captioned_files):
    """
    Bước 2: Đổi tên ảnh theo thứ tự 1.jpg, 2.jpg, ...
    Returns: dict mapping old_name -> new_name
    """
    print("\n" + "="*80)
    print("BƯỚC 2: ĐỔI TÊN ẢNH THEO THỨ TỰ")
    print("="*80)
    
    # Lấy danh sách ảnh còn lại (đã có caption)
    existing_images = get_existing_images()
    valid_images = [img for img in existing_images if img in captioned_files]
    
    print(f"\nSố ảnh cần đổi tên: {len(valid_images)}")
    
    # Tạo mapping old_name -> new_name
    rename_mapping = {}
    temp_dir = IMAGE_DIR / "temp_rename"
    temp_dir.mkdir(exist_ok=True)
    
    # Bước 2.1: Di chuyển tất cả ảnh sang thư mục tạm
    for old_name in valid_images:
        old_path = IMAGE_DIR / old_name
        temp_path = temp_dir / old_name
        if old_path.exists():
            shutil.move(str(old_path), str(temp_path))
    
    # Bước 2.2: Đổi tên và di chuyển về
    for idx, old_name in enumerate(valid_images, start=1):
        new_name = f"{idx}.jpg"
        rename_mapping[old_name] = new_name
        
        temp_path = temp_dir / old_name
        new_path = IMAGE_DIR / new_name
        
        if temp_path.exists():
            shutil.move(str(temp_path), str(new_path))
    
    # Xóa thư mục tạm
    temp_dir.rmdir()
    
    print(f"✓ Đã đổi tên {len(rename_mapping)} ảnh")
    
    return rename_mapping

def step3_update_metadata(rename_mapping):
    """
    Bước 3: Cập nhật file_name trong metadata.jsonl
    Returns: updated metadata entries
    """
    print("\n" + "="*80)
    print("BƯỚC 3: CẬP NHẬT METADATA")
    print("="*80)
    
    entries = load_metadata()
    updated_entries = []
    
    for entry in entries:
        old_name = entry['file_name']
        if old_name in rename_mapping:
            entry['file_name'] = rename_mapping[old_name]
            updated_entries.append(entry)
    
    # Sắp xếp theo file_name (1.jpg, 2.jpg, ...)
    updated_entries.sort(key=lambda x: int(x['file_name'].replace('.jpg', '')))
    
    print(f"✓ Đã cập nhật {len(updated_entries)} entries")
    
    return updated_entries

def step4_fix_caption_commas(entries):
    """
    Bước 4: Loại bỏ dấu phẩy sau "Ghibli style"
    """
    print("\n" + "="*80)
    print("BƯỚC 4: CHUẨN HÓA CAPTION")
    print("="*80)
    
    fixed_count = 0
    
    for entry in entries:
        caption = entry.get('text', '')
        
        # Kiểm tra và loại bỏ dấu phẩy sau "Ghibli style"
        if caption.startswith("Ghibli style,"):
            # Loại bỏ dấu phẩy và khoảng trắng thừa
            entry['text'] = "Ghibli style" + caption[len("Ghibli style,"):].lstrip()
            fixed_count += 1
    
    print(f"✓ Đã sửa {fixed_count} captions (loại bỏ dấu phẩy sau 'Ghibli style')")
    
    return entries

def save_metadata(entries):
    """Lưu metadata.jsonl"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"\n✓ Đã lưu {len(entries)} entries vào metadata.jsonl")

def verify_results():
    """Kiểm tra kết quả cuối cùng"""
    print("\n" + "="*80)
    print("KIỂM TRA KẾT QUẢ")
    print("="*80)
    
    # Đếm ảnh
    images = list(IMAGE_DIR.glob("*.jpg"))
    print(f"\nSố ảnh trong folder: {len(images)}")
    
    # Đếm metadata
    entries = load_metadata()
    print(f"Số entries trong metadata: {len(entries)}")
    
    # Kiểm tra khớp
    image_names = {img.name for img in images}
    metadata_names = {entry['file_name'] for entry in entries}
    
    missing_in_metadata = image_names - metadata_names
    missing_in_folder = metadata_names - image_names
    
    if missing_in_metadata:
        print(f"\n⚠ Ảnh không có trong metadata: {missing_in_metadata}")
    
    if missing_in_folder:
        print(f"\n⚠ Metadata không có ảnh tương ứng: {missing_in_folder}")
    
    if not missing_in_metadata and not missing_in_folder:
        print("\n✓ Tất cả ảnh và metadata đều khớp hoàn hảo!")
    
    # Kiểm tra caption format
    comma_count = sum(1 for e in entries if e.get('text', '').startswith('Ghibli style,'))
    print(f"\nCaption còn dấu phẩy sau 'Ghibli style': {comma_count}")
    
    # Hiển thị vài ví dụ
    print("\nVí dụ caption sau khi chuẩn hóa:")
    for i, entry in enumerate(entries[:3], 1):
        print(f"{i}. {entry['file_name']}: {entry['text'][:80]}...")

def main():
    print("="*80)
    print("SCRIPT DỌN DẸP VÀ CHUẨN HÓA DATASET")
    print("="*80)
    
    try:
        # Backup
        backup_path = backup_files()
        
        # Bước 1: Xóa ảnh không có caption
        captioned_files = step1_remove_images_without_caption()
        
        # Bước 2: Đổi tên ảnh
        rename_mapping = step2_rename_images_sequentially(captioned_files)
        
        # Bước 3: Cập nhật metadata
        updated_entries = step3_update_metadata(rename_mapping)
        
        # Bước 4: Fix caption commas
        fixed_entries = step4_fix_caption_commas(updated_entries)
        
        # Lưu metadata
        save_metadata(fixed_entries)
        
        # Kiểm tra
        verify_results()
        
        print("\n" + "="*80)
        print("HOÀN THÀNH!")
        print("="*80)
        print(f"\nBackup lưu tại: {backup_path}")
        print("Nếu cần khôi phục, copy các file từ backup về thư mục gốc.")
        
    except Exception as e:
        print(f"\n✗ LỖI: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
