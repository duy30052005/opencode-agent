import ast
import os
import re
from typing import List, Dict, Any
from langchain_core.tools import tool
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Khởi tạo Parser tĩnh (Cực nhẹ, không tốn RAM, Error-tolerant)
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

_IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', 'dist', 'build'}

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


# ---------------------------------------------------------
# HÀM 3: FIND REFERENCES (FR-05.2 — LSP Simulation)
# ---------------------------------------------------------
@tool
def find_references(symbol_name: str, directory: str = ".") -> str:
    """
    FR-05.2 LSP Simulation — Find References.
    Tìm tất cả các vị trí trong workspace mà một hàm/biến/class được SỬ DỤNG
    (không phải nơi định nghĩa). Rất hữu ích để hiểu impact khi refactor.

    Args:
        symbol_name: Tên hàm, class hoặc biến cần tìm reference.
        directory:   Thư mục gốc để tìm kiếm (mặc định là thư mục hiện tại).
    """
    results: List[str] = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS and not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            lines = source.splitlines()
            for node in ast.walk(tree):
                # Bắt các lần gọi hàm: symbol_name(...)
                if isinstance(node, ast.Call):
                    func = node.func
                    name = None
                    if isinstance(func, ast.Name):
                        name = func.id
                    elif isinstance(func, ast.Attribute):
                        name = func.attr
                    if name == symbol_name:
                        ln = node.lineno
                        snippet = lines[ln - 1].strip() if ln <= len(lines) else ''
                        results.append(f"{fpath}:{ln}  →  {snippet}")
                # Bắt các lần dùng biến/class: Name(id=symbol_name)
                elif isinstance(node, ast.Name) and node.id == symbol_name:
                    # Bỏ qua các nơi ĐỊNH NGHĨA (FunctionDef, ClassDef, arg)
                    ln = node.lineno
                    snippet = lines[ln - 1].strip() if ln <= len(lines) else ''
                    ref_str = f"{fpath}:{ln}  →  {snippet}"
                    if ref_str not in results:
                        results.append(ref_str)

    if not results:
        return f"Không tìm thấy reference nào đến '{symbol_name}' trong '{directory}'."
    if len(results) > 50:
        return f"Tìm thấy >{len(results)} kết quả. 50 đầu tiên:\n" + "\n".join(results[:50])
    return f"=== REFERENCES của [{symbol_name}] ({len(results)} kết quả) ===\n" + "\n".join(results)


# ---------------------------------------------------------
# HÀM 4: GO TO DEFINITION (FR-05.2 — LSP Simulation)
# ---------------------------------------------------------
@tool
def go_to_definition(symbol_name: str, directory: str = ".") -> str:
    """
    FR-05.2 LSP Simulation — Go To Definition.
    Tìm chính xác nơi một hàm (def) hoặc class (class) được ĐỊNH NGHĨA trong workspace.
    Trả về đường dẫn file + số dòng + signature đầy đủ.

    Args:
        symbol_name: Tên hàm hoặc class cần tìm định nghĩa.
        directory:   Thư mục gốc để tìm kiếm (mặc định là thư mục hiện tại).
    """
    results: List[str] = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS and not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            lines = source.splitlines()
            for node in ast.walk(tree):
                node_name = None
                kind = None
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    node_name = node.name
                    kind = 'async def' if isinstance(node, ast.AsyncFunctionDef) else 'def'
                elif isinstance(node, ast.ClassDef):
                    node_name = node.name
                    kind = 'class'

                if node_name == symbol_name:
                    ln = node.lineno
                    signature = lines[ln - 1].strip() if ln <= len(lines) else ''
                    results.append(
                        f"📍 [{kind}] {fpath}:{ln}\n   {signature}"
                    )

    if not results:
        return f"Không tìm thấy định nghĩa nào cho '{symbol_name}' trong '{directory}'."
    return (
        f"=== DEFINITION của [{symbol_name}] ({len(results)} kết quả) ===\n"
        + "\n\n".join(results)
    )


# Xuất danh sách tools để LangGraph (workflow.py) sử dụng
# (replace_tools được import riêng để tránh circular import)
from .replace_tools import replace_in_file, preview_patch  # noqa: E402

coding_tools = [
    analyze_code_structure,
    discover_symbols,
    find_references,
    go_to_definition,
    replace_in_file,
    preview_patch,
]