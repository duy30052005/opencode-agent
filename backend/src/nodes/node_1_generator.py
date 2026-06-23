from .base_node import BaseNode
from src.schemas.node_1_schema import Node1Input, Node1Output
from src.core import llm_client
from src.tools.ast_tools import analyze_code_structure
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

        if retry_count < 1:
            prompt = self._get_new_code_prompt(requirement)
            response = llm_client.llm.invoke([("user", prompt)])
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
            # Triệt tiêu trí nhớ cũ, ép AI đối diện với hiện tại
            response = llm_client.llm.invoke([("user", prompt)])

        raw_content = response.content
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
            "messages": [response],
            "metadata": state["metadata"],
            "state": new_state, # Trả về bản state đã được bọc lót kỹ càng
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
        # Regex thông minh: 
        # Bắt giữa bằng ==== hoặc REPLACE. 
        # Bắt cuối bằng >>>> REPLACE hoặc dấu kết thúc code block ``` hoặc hết chuỗi \Z
        pattern = re.compile(
            r"<<<< SEARCH\s*\n(.*?)\n\s*(?:====+|REPLACE)\s*\n(.*?)(?:\n\s*>>>> REPLACE|\n\s*```|\Z)", 
            re.DOTALL
        )
        
        patches = pattern.findall(llm_response)
        if not patches:
            print(f"\n[Cảnh báo Node 1] LLM có trả về <<<< SEARCH nhưng format sai. Regex không bắt được!")
            return original_code 
            
        patched_code = original_code
        for search_block, replace_block in patches:
            sb_stripped = search_block.strip()
            # Dọn dẹp dấu ``` thừa ở cuối replace_block nếu có
            rb_stripped = replace_block.replace("```", "").strip() 
            
            if sb_stripped in patched_code:
                patched_code = patched_code.replace(sb_stripped, rb_stripped)
            else:
                print(f"\n[Cảnh báo Node 1] Khối SEARCH không khớp với code hiện tại!")
                
        return patched_code
    
    def _get_new_code_prompt(self, requirement: str) -> str:
        return f"""You are an expert Python developer.

Requirement: 
{requirement}

CRITICAL RULES:
1. NO YAPPING. Do not include explanations.
2. Output ONLY the raw Python code inside a markdown block.
3. DO NOT use the `input()` function."""

    def _get_fix_code_prompt(self, requirement: str, code: str, stderr: str, ast_info: str) -> str:
        # 🚀 SỬA LỖI 1: FORMAT VÍ DỤ CHUẨN XÁC CÓ DẤU ==== VÀ >>>> REPLACE
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

NO YAPPING. Do not explain the bug.

DO NOT rewrite the entire file. You MUST use the SEARCH/REPLACE block format to edit the code.

The code in the SEARCH block MUST match the "Previous Code" EXACTLY, character for character, including indentation.

EXECUTION IS GROUND TRUTH: If there is a conflict between the original requirement and the error logs/test failures from the execution environment, you MUST prioritize fixing the code to pass the execution tests. The test logs are the absolute truth.

FORMAT EXAMPLE:
<<<< SEARCH
def old_function():
return False
def old_function():
    return True
REPLACE
"""