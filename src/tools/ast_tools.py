import os
from langchain_core.tools import tool
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Khởi tạo Parser tĩnh (Cực nhẹ, không tốn RAM, Error-tolerant)
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

# ---------------------------------------------------------
# HÀM 1: PHÂN TÍCH CODE TRONG BỘ NHỚ (In-memory)
# ---------------------------------------------------------
@tool
def analyze_code_structure(code_content: str) -> str:
    """
    Sử dụng công cụ này khi bạn nhận được thông báo lỗi từ Sandbox nhưng không rõ cấu trúc file hiện tại.
    Công cụ này phân tích mã nguồn và trả về danh sách chính xác các hàm (functions) và lớp (classes) 
    cùng với tọa độ dòng của chúng, giúp bạn định vị lỗi nhanh hơn.
    """
    if not code_content or code_content.strip() == "":
        return "Lỗi: Không có mã nguồn để phân tích."

    try:
        tree = parser.parse(bytes(code_content, "utf8"))
        root_node = tree.root_node
    except Exception as e:
        return f"Lỗi khi parse AST: {str(e)}"

    analysis_result = ["--- BÁO CÁO CẤU TRÚC MÃ NGUỒN ---"]
    
    for node in root_node.children:
        if node.type == 'function_definition':
            func_name = node.child_by_field_name('name').text.decode('utf8')
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            analysis_result.append(f"🔹 Function: `{func_name}` (Dòng {start_line} - {end_line})")
            
        elif node.type == 'class_definition':
            class_name = node.child_by_field_name('name').text.decode('utf8')
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            analysis_result.append(f"📦 Class: `{class_name}` (Dòng {start_line} - {end_line})")

    if len(analysis_result) == 1:
        analysis_result.append("Không tìm thấy khai báo hàm hoặc lớp nào trong đoạn code.")

    return "\n".join(analysis_result)


# ---------------------------------------------------------
# HÀM 2: CHỤP X-QUANG FILE (FR-05.2)
# ---------------------------------------------------------
@tool
def discover_symbols(file_path: str) -> str:
    """
    Công cụ chụp X-Quang cấu trúc file Python (FR-05.2).
    Sử dụng khi bạn cần biết nhanh trong một file vật lý bên ngoài chứa những Class và Hàm nào.
    """
    if not os.path.exists(file_path):
        return f"Lỗi: Không tìm thấy file tại '{file_path}'"
        
    if not file_path.endswith('.py'):
        return f"Lỗi: Công cụ này hiện tại chỉ hỗ trợ Python (.py)."

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        tree = parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        
        symbols = []
        for node in root_node.children:
            # Quét Class
            if node.type == 'class_definition':
                class_name = node.child_by_field_name('name').text.decode('utf8')
                symbols.append(f"📦 Class: {class_name}")
                
                # Quét các hàm bên trong Class
                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        if child.type == 'function_definition':
                            func_name = child.child_by_field_name('name').text.decode('utf8')
                            symbols.append(f"   ├─ Hàm: {func_name}")
                            
            # Quét Hàm tự do
            elif node.type == 'function_definition':
                func_name = node.child_by_field_name('name').text.decode('utf8')
                symbols.append(f"⚙️ Hàm tự do: {func_name}")
                
        if not symbols:
            return f"File '{file_path}' không chứa định nghĩa Class hay Hàm nào."
            
        return f"=== CẤU TRÚC SYMBOL CỦA [{file_path}] ===\n" + "\n".join(symbols)
        
    except Exception as e:
        return f"Lỗi đọc file: {str(e)}"
# Xuất danh sách tools để LangGraph (workflow.py) sử dụng
coding_tools = [analyze_code_structure, discover_symbols]