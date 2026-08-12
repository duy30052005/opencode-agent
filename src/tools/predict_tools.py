import ast
import os
from langchain_core.tools import tool
# Import llm_client từ core của bạn để dùng làm AI dự đoán
from src.core import llm_client 

@tool
def predict_function_meaning(file_path: str, function_name: str) -> str:
    """
    Công cụ Dự đoán Ý nghĩa Hàm (FR-05.3).
    Dùng công cụ này khi bạn đã biết tên một hàm nhưng nó quá dài hoặc không có tài liệu (docstring), 
    cần phân tích xem nó nhận input gì, xử lý logic gì và trả về output gì.
    
    Args:
        file_path: Đường dẫn tới file chứa hàm.
        function_name: Tên của hàm cần phân tích (VD: "get_pagination_range").
    """
    if not os.path.exists(file_path):
        return f"Lỗi: Không tìm thấy file tại '{file_path}'"

    try:
        # 1. Đọc mã nguồn file
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        tree = ast.parse(source_code)
        function_node = None

        # 2. Dùng AST duyệt cây cú pháp để tìm chính xác hàm được yêu cầu
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                function_node = node
                break
            elif isinstance(node, ast.AsyncFunctionDef) and node.name == function_name:
                function_node = node
                break

        if not function_node:
            return f"Lỗi: Không tìm thấy hàm '{function_name}' trong file '{file_path}'."

        # 3. Trích xuất đúng mã nguồn của hàm đó (không lấy thừa mã nguồn bên ngoài)
        func_source = ast.get_source_segment(source_code, function_node)
        if not func_source:
            return "Lỗi: Không thể trích xuất đoạn code của hàm này."

        # 4. Nhờ LLM đóng vai trò "Kỹ sư phân tích" tóm tắt lại hàm
        prompt = f"""Bạn là một kỹ sư phần mềm lão luyện. Hãy đọc hàm Python sau và trả về một tài liệu tóm tắt ngắn gọn nhất có thể:
        1. Mục đích chính: Hàm này dùng để làm gì?
        2. Đầu vào (Inputs): Ý nghĩa các tham số.
        3. Đầu ra (Outputs): Nó trả về cái gì?
        4. Cảnh báo (Edge cases): Có lỗi tiềm ẩn hay xử lý đặc biệt nào không?

        MÃ NGUỒN CẦN PHÂN TÍCH:
        ```python
        {func_source}
        ```
        """
        
        # Gọi API để sinh tóm tắt
        response = llm_client.llm.invoke(prompt)
        
        return f"=== Ý NGHĨA HÀM [{function_name}] ===\n{response.content}"

    except SyntaxError as e:
        return f"Lỗi cú pháp (SyntaxError) không thể đọc file '{file_path}': {e}"
    except Exception as e:
        return f"Lỗi khi dự đoán ý nghĩa hàm: {str(e)}"

# ==========================================
# TEST NHANH Ở LOCAL
# ==========================================
if __name__ == "__main__":
    print("--- ĐANG TEST FR-05.3 PREDICT FUNCTION MEANING ---")
    # Thử yêu cầu nó dự đoán chính cái hàm _apply_patch mà bạn vừa vất vả viết ra
    print(predict_function_meaning.invoke({
        "file_path": "src/nodes/node_1_generator.py", 
        "function_name": "_apply_patch"
    }))