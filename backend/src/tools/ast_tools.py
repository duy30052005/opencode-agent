from langchain_core.tools import tool
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Khởi tạo Parser tĩnh (Cực nhẹ, không tốn RAM như LSP Server)
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

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
        # Tree-sitter yêu cầu bytes
        tree = parser.parse(bytes(code_content, "utf8"))
        root_node = tree.root_node
    except Exception as e:
        return f"Lỗi khi parse AST: {str(e)}"

    analysis_result = ["--- BÁO CÁO CẤU TRÚC MÃ NGUỒN ---"]
    
    # Duyệt AST để tìm các function và class
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

# Xuất danh sách tools để LangGraph sử dụng
coding_tools = [analyze_code_structure]