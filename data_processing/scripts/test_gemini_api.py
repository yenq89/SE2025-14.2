"""
Test Gemini API Keys
====================
Quick script to verify that your Gemini API keys are working correctly.

Usage:
    python test_gemini_api.py

Requirements:
    - .env file with GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
    - google-generativeai package installed
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_api_key(key_number, api_key):
    """
    Test a single API key by making a simple request.
    
    Args:
        key_number: The key number (1, 2, 3, etc.)
        api_key: The API key to test
        
    Returns:
        True if the key works, False otherwise
    """
    if not api_key or api_key == "your_api_key_here" or api_key.startswith("your_"):
        print(f"❌ Key #{key_number}: CHƯA CẤU HÌNH (vui lòng cập nhật .env)")
        return False
    
    try:
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Try the primary model (gemini-2.5-flash)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Make a simple test request
        response = model.generate_content("Say 'API key is working' in one sentence.")
        
        if response and response.text:
            print(f"✅ Key #{key_number}: HOẠT ĐỘNG!")
            print(f"   Response: {response.text.strip()[:50]}...")
            return True
        else:
            print(f"⚠ Key #{key_number}: Không nhận được response")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "API key not valid" in error_msg or "Invalid API key" in error_msg:
            print(f"❌ Key #{key_number}: KHÔNG HỢP LỆ (kiểm tra lại key)")
        elif "quota" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
            print(f"⚠ Key #{key_number}: ĐÃ HẾT QUOTA (chờ 24h hoặc dùng key khác)")
        elif "rate_limit" in error_msg.lower():
            print(f"⚠ Key #{key_number}: RATE LIMIT (thử lại sau vài giây)")
        else:
            print(f"❌ Key #{key_number}: LỖI - {error_msg[:100]}")
        return False

def main():
    """Main function to test all API keys from .env file."""
    print("=" * 60)
    print("🔑 TEST GEMINI API KEYS")
    print("=" * 60)
    print()
    
    # Load environment variables
    if not os.path.exists('.env'):
        print("❌ KHÔNG TÌM THẤY FILE .env!")
        print()
        print("Hướng dẫn:")
        print("1. Copy file .env.example:")
        print("   Copy-Item .env.example .env")
        print()
        print("2. Chỉnh sửa file .env và thêm API keys của bạn")
        print()
        print("3. Chạy lại script này:")
        print("   python test_gemini_api.py")
        print()
        return False
    
    load_dotenv()
    
    # Test each key
    results = []
    for i in range(1, 6):  # Test up to 5 keys
        api_key = os.getenv(f"GEMINI_API_KEY_{i}")
        
        if api_key:
            result = test_api_key(i, api_key)
            results.append((i, result))
            print()
        else:
            # Only show "not configured" for keys 1-3 (recommended)
            if i <= 3:
                print(f"⚪ Key #{i}: Chưa cấu hình (khuyến nghị thêm key)")
                print()
    
    # Summary
    print("=" * 60)
    print("📊 KẾT QUẢ TỔNG HỢP")
    print("=" * 60)
    
    working_keys = sum(1 for _, result in results if result)
    total_keys = len(results)
    
    print(f"✅ Keys hoạt động: {working_keys}/{total_keys}")
    
    if working_keys == 0:
        print()
        print("⚠ CẢNH BÁO: Không có key nào hoạt động!")
        print("Pipeline sẽ không thể chạy. Vui lòng:")
        print("1. Kiểm tra lại API keys trong file .env")
        print("2. Đảm bảo keys chưa hết quota")
        print("3. Lấy keys mới tại: https://aistudio.google.com/apikey")
        return False
    elif working_keys == 1:
        print()
        print("⚠ KHUYẾN NGHỊ: Chỉ có 1 key hoạt động")
        print("Nên thêm 1-2 keys nữa để tránh gián đoạn khi hết quota")
    else:
        print()
        print(f"✅ TỐT! Bạn có {working_keys} keys hoạt động")
        print("Pipeline sẽ tự động chuyển đổi giữa các keys khi cần")
    
    print()
    print("=" * 60)
    print("Sẵn sàng chạy pipeline!")
    print("Chạy: python pipeline_build_caption.py")
    print("=" * 60)
    
    return working_keys > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Đã hủy bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ LỖI KHÔNG MONG MUỐN: {e}")
        sys.exit(1)
