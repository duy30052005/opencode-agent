import os
import re
from langchain_core.tools import tool

@tool
def grep_search(search_term: str, directory: str = ".", file_extension: str = ".py") -> str:
    """
    Tìm kiếm một chuỗi hoặc Regex trong các file thuộc một thư mục.
    Rất hữu ích để tìm vị trí định nghĩa hàm, class hoặc biến.
    
    Args:
        search_term: Từ khóa hoặc Regex cần tìm (vd: "def is_prime" hoặc "class User").
        directory: Thư mục để bắt đầu tìm kiếm (mặc định là thư mục hiện tại ".").
        file_extension: Đuôi file cần quét (vd: ".py", ".js", ".java" hoặc để trống "" quét hết).
    """
    results = []
    
    try:
        # Biên dịch regex để tìm kiếm (bỏ qua phân biệt hoa thường)
        pattern = re.compile(search_term, re.IGNORECASE)
        
        for root, dirs, files in os.walk(directory):
            # Bỏ qua các thư mục rác, ẩn
            if any(part.startswith('.') or part in ['__pycache__', 'node_modules', 'venv', 'target'] for part in root.split(os.sep)):
                continue
                
            for file in files:
                if file_extension and not file.endswith(file_extension):
                    continue
                    
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                # Trả về định dạng: ./path/to/file.py:45 -> nội dung dòng code
                                clean_line = line.strip()
                                results.append(f"{file_path}:{line_num} -> {clean_line}")
                except (UnicodeDecodeError, PermissionError):
                    # Bỏ qua các file nhị phân (ảnh, pdf, db) hoặc không có quyền đọc
                    continue
                    
        if not results:
            return f"Không tìm thấy '{search_term}' trong thư mục {directory}."
            
        # Giới hạn kết quả trả về để không làm tràn bộ nhớ (Context Window) của LLM
        if len(results) > 50:
            return "Tìm thấy quá nhiều kết quả (>50). Dưới đây là 50 kết quả đầu tiên:\n" + "\n".join(results[:50])
            
        return "\n".join(results)
        
    except Exception as e:
        return f"Lỗi khi chạy Grep Search: {str(e)}"

# Code test nhanh cục bộ (Chỉ chạy khi bạn gọi trực tiếp file này)
if __name__ == "__main__":
    print("--- ĐANG TEST GREP TOOL ---")
    # Thử tìm chữ "is_success" trong thư mục src
    print(grep_search.invoke({"search_term": "is_success", "directory": "src", "file_extension": ".py"}))