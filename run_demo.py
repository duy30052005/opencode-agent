"""
run_demo.py — Entry point đơn giản để test trực tiếp luồng OpenCode Agent.

Cách chạy:
    python run_demo.py
"""

import os
import sys

# Ép hệ thống dùng chuẩn UTF-8 trên Windows để tránh lỗi Unicode (chữ Đ, á, ớ...)
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Import thẳng hàm run_agent từ engine thay vì đi đường vòng qua Typer app
from src.cli.runner import run_agent

def main():
    # Test case "tử huyệt" để ép LLM phải gọi Tool quét AST
    requirement = (
        "Viết một class `BankSystem` chứa 2 class con, bên trong có các hàm giao dịch, "
        "nhưng tao muốn mày cố tình viết code bị sai thụt lề (indentation error) "
        "hoặc gọi sai tên hàm nội bộ để test công cụ sửa lỗi."
    )

    print("-" * 60)
    print(f"🚀 BẮT ĐẦU CHẠY TEST ĐỘC LẬP\n📝 Yêu cầu: {requirement}")
    print("-" * 60)
    
    # Kích hoạt Agent (Tối đa 3 lần thử)
    try:
        run_agent(requirement=requirement, max_retries=3)
    except KeyboardInterrupt:
        print("\n[!] Đã ép dừng hệ thống bằng Ctrl+C.")
    except Exception as e:
        print(f"\n[!] Lỗi Crash Hệ Thống: {e}")

if __name__ == "__main__":
    main()