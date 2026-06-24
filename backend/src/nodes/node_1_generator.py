from .base_node import BaseNode
from src.schemas.node_1_schema import Node1Input, Node1Output
from src.core import llm_client
from src.tools.ast_tools import analyze_code_structure, discover_symbols
from src.tools.search_tools import grep_search
from src.tools.predict_tools import predict_function_meaning
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
import time
import re

class CodeGenerator(BaseNode):
    NODE_NAME = "code_generator"

    def __call__(self, state: Node1Input) -> Node1Output:
        start_time = time.perf_counter()
        
        requirement = state["state"]["requirement"]
        retry_count = state["state"].get("retry_count", 0)
        
        # Tạo một bản sao độc lập, tuyệt đối không tham chiếu con trỏ cũ
        new_state = {}
        for k, v in state["state"].items():
            if isinstance(v, dict):
                new_state[k] = v.copy()
            elif isinstance(v, list):
                new_state[k] = list(v)
            else:
                new_state[k] = v

        # 1. CHUẨN BỊ PROMPT BAN ĐẦU
        if retry_count < 1:
            prompt = self._get_new_code_prompt(requirement)
        else:
            # LẤY CODE GỐC TỪ LẦN CHẠY TRƯỚC ĐỂ VÁ
            code = new_state.get("code", "")
            exec_result = new_state.get("execution_result", {})
            test_cases = exec_result.get("test_cases", [])
            failed_tests = [tc for tc in test_cases if not tc.get("passed", True)]
            
            if failed_tests:
                stderr = "TEST LOGIC FAILED:\n" + "\n".join(
                    [f"- Input: {tc.get('input')} | Expected: {tc.get('expected_output')} | Got: {tc.get('actual_output')}" for tc in failed_tests[:3]]
                )
            else:
                stderr = exec_result.get("stderr", "") or ""
            
            ast_info = "Không có mã nguồn để phân tích."
            if code:
                try:
                    ast_info = analyze_code_structure.invoke(code)
                except Exception as e:
                    ast_info = f"Lỗi AST: {e}"
            
            prompt = self._get_fix_code_prompt(requirement, code, stderr, ast_info)

        # 2. TRANG BỊ BỘ 3 TOOL VÀ KHỞI TẠO VÒNG LẶP SUY NGHĨ (AGENTIC LOOP)
        llm_with_tools = llm_client.llm.bind_tools([grep_search, discover_symbols, predict_function_meaning])
        
        messages = [HumanMessage(content=prompt)]
        final_content = ""
        final_response = None

        # Cho phép AI suy nghĩ và dùng tool tối đa 4 bước
        for step in range(4):
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            final_response = response

            # Nếu LLM không gọi Tool nào nữa, tức là đã chốt code/patch
            if not response.tool_calls:
                final_content = response.content
                break

            # Bộ định tuyến thực thi Tool (Tool Executor)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                print(f"\n 🔍 [Agent Tool] Đang sử dụng công cụ: '{tool_name}'...")
                
                try:
                    if tool_name == "grep_search":
                        tool_result = grep_search.invoke(tool_args)
                    elif tool_name == "discover_symbols":
                        tool_result = discover_symbols.invoke(tool_args)
                    elif tool_name == "predict_function_meaning":
                        tool_result = predict_function_meaning.invoke(tool_args)
                    else:
                        tool_result = f"Lỗi: Tool '{tool_name}' không tồn tại."
                except Exception as e:
                    tool_result = f"Lỗi khi chạy tool {tool_name}: {e}"
                
                # Trả kết quả đọc được lại cho não LLM phân tích
                messages.append(ToolMessage(
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                    content=str(tool_result)
                ))

        # Đảm bảo lấy nội dung cuối cùng
        if not final_content and final_response:
            final_content = final_response.content or ""

        # 3. XỬ LÝ OUTPUT NHƯ CŨ
        raw_content = final_content
        code_content = "".join([block["text"] if isinstance(block, dict) and "text" in block else str(block) for block in raw_content]) if isinstance(raw_content, list) else str(raw_content)

        # THỰC HIỆN VÁ VÀ ÉP CẬP NHẬT VÀO STATE ĐỘC LẬP
        if retry_count > 0 and "<<<< SEARCH" in code_content:
            old_code = new_state.get("code", "")
            patched = self._apply_patch(old_code, code_content)
            new_state["code"] = patched
        else:
            new_state["code"] = self._extract_code(code_content)
        
        # Cập nhật số lần thử để các node sau không bị lệch nhịp
        new_state["retry_count"] = retry_count + 1

        action = {
            "next_node": "code_executor",
            "message": "Đã xử lý mã nguồn và cập nhật trạng thái độc lập.",
            "reasoning": "Chuyển thẳng sang Sandbox để thực thi."
        }

        output = {
            "messages": [final_response], 
            "metadata": state["metadata"],
            "state": new_state,
            "action": action
        }

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        self.write_history(output, state, output, duration_ms=duration_ms)
        return output

    def _extract_code(self, code_content: str) -> str:
        if "```python" in code_content:
            return code_content.split("```python")[1].split("```")[0].strip()
        return code_content.strip()

    def _apply_patch(self, original_code: str, llm_response: str) -> str:
        """
        Áp dụng bản vá cục bộ bằng định dạng SEARCH/REPLACE.
        Đã được nâng cấp để khoan dung với lỗi định dạng từ LLM (Fault-tolerant).
        """
        import re
        
        # 🌟 CẢI TIẾN CHÍ MẠNG: 
        # Thay vì ép buộc kết thúc bằng '>>>> REPLACE', ta dùng '>>>>.*' 
        # để chấp nhận việc LLM viết thiếu (chỉ viết >>>>) hoặc viết sai chính tả.
        pattern = re.compile(
            r"<<<< SEARCH\s*\n(.*?)\n\s*(?:====+|REPLACE)\s*\n(.*?)(?:\n\s*>>>>.*|\n\s*```|\Z)", 
            re.DOTALL
        )
        
        patches = pattern.findall(llm_response)
        
        if not patches:
            # Nếu không tìm thấy khối patch nào, trả về chính llm_response 
            # (Đề phòng trường hợp LLM sinh lại toàn bộ code ở dạng thường)
            clean_code = llm_response.replace("```python", "").replace("```", "").strip()
            return clean_code

        modified_code = original_code if original_code else ""
        
        for search_block, replace_block in patches:
            search_block = search_block.strip()
            # Dọn dẹp các ký tự thừa bị dính vào do lỗi format của LLM
            replace_block = replace_block.replace("```", "").strip()
            
            if search_block in modified_code:
                modified_code = modified_code.replace(search_block, replace_block)
            else:
                # Fallback: Nếu không tìm thấy đoạn SEARCH chính xác từng khoảng trắng,
                # ta thử dọn dẹp khoảng trắng dòng đầu/cuối để match dính.
                search_lines = search_block.splitlines()
                if search_lines and search_lines[0] in modified_code:
                    # Logic tìm kiếm tương đối nếu cần (có thể mở rộng sau)
                    pass

        return modified_code
    
    def _get_new_code_prompt(self, requirement: str) -> str:
        return f"""You are an expert Python developer with access to codebase search tools.
If you need to understand the project structure before writing code, USE YOUR TOOLS:
1. `grep_search`: Find where a keyword, function, or class is defined.
2. `discover_symbols`: View the outline (classes/functions) of a specific file.
3. `predict_function_meaning`: Read and summarize the logic of a complex function.

Requirement: 
{requirement}

CRITICAL RULES:
1. NO YAPPING. Do not include explanations.
2. Output ONLY the raw Python code inside a markdown block.
3. DO NOT use the `input()` function."""

    def _get_fix_code_prompt(self, requirement: str, code: str, stderr: str, ast_info: str) -> str:
        return f"""The previous code failed. 
Below is the Abstract Syntax Tree (AST) structure of the broken code to help you navigate:

--- AST STRUCTURE ---
{ast_info}
---------------------

Original Requirement: 
{requirement}

Previous Code: 
```python
{code}
Error Message / Test Failures:
{stderr}

CRITICAL RULES FOR BUG FIXING:
If the error relates to a missing variable, incorrect API call, or unknown function from another file, USE YOUR TOOLS (grep_search, discover_symbols, predict_function_meaning) to investigate before writing the fix.

NO YAPPING. Do not explain the bug.

DO NOT rewrite the entire file. You MUST use the SEARCH/REPLACE block format to edit the code.
The code in the SEARCH block MUST match the "Previous Code" EXACTLY.

FORMAT EXAMPLE:
<<<< SEARCH
def old_function():
return False
def old_function():
return True

REPLACE
"""