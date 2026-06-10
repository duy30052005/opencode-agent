import copy
from datetime import datetime, timezone

class BaseNode:
    NODE_NAME: str

    def write_history(self, state: dict, input_data: dict, output_data: dict, duration_ms: int) -> dict:
        # 1. Tạo bản sao an toàn và loại bỏ 'history' để tránh lỗi Circular Reference
        safe_input = copy.deepcopy(input_data)
        if "state" in safe_input and "history" in safe_input["state"]:
            del safe_input["state"]["history"]

        safe_output = copy.deepcopy(output_data)
        if "state" in safe_output and "history" in safe_output["state"]:
            del safe_output["state"]["history"]

        # 2. Tạo bản ghi lịch sử
        history_entry = {
            "attempt": state["state"].get("retry_count", 0) + 1,
            "node": self.NODE_NAME,
            "input": safe_input,
            "output": safe_output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms
        }

        # 3. Thêm vào mảng history chính thức
        if "history" not in state["state"]:
            state["state"]["history"] = []
            
        state["state"]["history"].append(history_entry)

        return history_entry