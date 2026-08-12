"""
replace_tools.py — FR-05.4 Replace Tool & FR-05.5 Patch Preview
Cho phép Agent tìm kiếm và thay thế nội dung trong file thực,
kèm preview diff trước khi ghi.
"""
from __future__ import annotations

import difflib
import os
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


# ─────────────────────────────────────────────────────────────────────────────
# FR-05.4: Replace Tool
# ─────────────────────────────────────────────────────────────────────────────

@tool
def replace_in_file(file_path: str, search: str, replace: str) -> str:
    """
    FR-05.4 Replace Tool: Tìm kiếm chính xác đoạn `search` trong file và thay thế
    bằng `replace`. Trước khi ghi, công cụ sẽ sinh patch preview (diff) để bạn
    xem xét thay đổi.

    Args:
        file_path: Đường dẫn đến file cần chỉnh sửa (ví dụ: "src/utils.py").
        search:    Đoạn code CHÍNH XÁC cần tìm (bao gồm cả khoảng trắng/indent).
        replace:   Đoạn code mới để thay thế vào vị trí tìm thấy.
    
    Returns:
        Chuỗi mô tả kết quả: diff preview nếu thành công, thông báo lỗi nếu thất bại.
    """
    if not os.path.isfile(file_path):
        return f"❌ Lỗi FR-05.4: Không tìm thấy file '{file_path}'."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
    except (PermissionError, OSError) as e:
        return f"❌ Lỗi FR-05.4: Không thể đọc file '{file_path}': {e}"

    if search not in original_content:
        # Thử match sau khi normalize khoảng trắng dòng
        stripped_lines_orig = "\n".join(l.rstrip() for l in original_content.splitlines())
        stripped_lines_search = "\n".join(l.rstrip() for l in search.splitlines())
        if stripped_lines_search in stripped_lines_orig:
            new_content = stripped_lines_orig.replace(stripped_lines_search, replace)
        else:
            return (
                f"❌ Lỗi FR-05.4: Không tìm thấy đoạn code sau trong '{file_path}':\n"
                f"```\n{search[:300]}\n```\n"
                "Hãy dùng `grep_search` hoặc `discover_symbols` để tìm đoạn code chính xác."
            )
    else:
        new_content = original_content.replace(search, replace, 1)

    # FR-05.5: Sinh patch preview (diff)
    diff_lines = list(difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        n=3,
    ))

    # Ghi file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except (PermissionError, OSError) as e:
        return f"❌ Lỗi FR-05.4: Không thể ghi vào file '{file_path}': {e}"

    if diff_lines:
        diff_text = "".join(diff_lines)
        return (
            f"✅ FR-05.4: Đã thay thế thành công trong '{file_path}'.\n\n"
            f"📋 Patch Preview (FR-05.5):\n"
            f"```diff\n{diff_text}\n```"
        )
    return f"✅ FR-05.4: Thay thế hoàn tất trong '{file_path}' (không có thay đổi diff)."


# ─────────────────────────────────────────────────────────────────────────────
# FR-05.5: Patch Preview (standalone, không ghi file)
# ─────────────────────────────────────────────────────────────────────────────

@tool
def preview_patch(file_path: str, search: str, replace: str) -> str:
    """
    FR-05.5 Patch Preview: Xem trước sự thay đổi sẽ xảy ra nếu thực hiện replace,
    mà KHÔNG ghi vào file. Dùng để kiểm tra trước khi dùng replace_in_file.

    Args:
        file_path: Đường dẫn đến file (ví dụ: "src/main.py").
        search:    Đoạn code hiện tại cần thay thế.
        replace:   Đoạn code mới sẽ thay vào.

    Returns:
        Unified diff dạng text, hiển thị - (dòng xóa) và + (dòng thêm).
    """
    if not os.path.isfile(file_path):
        return f"❌ Không tìm thấy file '{file_path}'."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original = f.read()
    except OSError as e:
        return f"❌ Không thể đọc file: {e}"

    if search not in original:
        return (
            f"⚠️ Không tìm thấy đoạn SEARCH trong '{file_path}'.\n"
            "Không thể tạo preview. Dùng grep_search để tìm đoạn code chính xác."
        )

    new_content = original.replace(search, replace, 1)
    diff_lines = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        n=3,
    ))

    if not diff_lines:
        return "ℹ️ Không có thay đổi nào (search và replace giống nhau)."

    diff_text = "".join(diff_lines)
    return f"📋 Patch Preview cho '{file_path}':\n```diff\n{diff_text}\n```"


# Danh sách tool export (dùng trong workflow)
replace_tools = [replace_in_file, preview_patch]


if __name__ == "__main__":
    # Quick smoke test
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                     delete=False, encoding="utf-8") as tmp:
        tmp.write("def greet():\n    print('Hello World')\n")
        tmp_path = tmp.name

    print("--- PREVIEW TEST ---")
    print(preview_patch.invoke({
        "file_path": tmp_path,
        "search": "    print('Hello World')",
        "replace": "    print('Hello, Agent!')",
    }))

    print("\n--- REPLACE TEST ---")
    print(replace_in_file.invoke({
        "file_path": tmp_path,
        "search": "    print('Hello World')",
        "replace": "    print('Hello, Agent!')",
    }))

    os.unlink(tmp_path)
