import uuid
import json
from datetime import datetime, timezone

# Import đồ thị từ phần thư mục src
from src.core.workflow import app

def run_agent(requirement: str):
    print("="*60)
    print(f"🚀 BẮT ĐẦU TASK: {requirement}")
    print("="*60)
    
    # 1. Khởi tạo Input State tuân thủ ĐÚNG định dạng AgentState
    initial_state = {
        "metadata": {
            "task_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "llm_model": "gemini-2.5-flash"
        },
        "state": {
            "requirement": requirement,
            "code": None,
            "execution_result": {
                "status": "pending",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "execution_time_ms": 0,
                "test_cases": []
            },
            "is_success": False,
            "retry_count": 0,
            "max_retries": 3,
            "history": []
        },
        "action": None
    }

    # 2. Gọi LangGraph thực thi
    final_state = app.invoke(initial_state)

    # 3. In kết quả cuối cùng
    print("\n" + "="*60)
    print("🎉 KẾT QUẢ CUỐI CÙNG TỪ HỆ THỐNG")
    print("="*60)
    
    state_data = final_state["state"]
    action_data = final_state.get("action", {})
    
    print(f"✅ Trạng thái tổng: {'THÀNH CÔNG' if state_data['is_success'] else 'THẤT BẠI'}")
    print(f"🔄 Số lần đã thử: {state_data['retry_count']}")
    print(f"💬 Thông báo từ Node 3: {action_data.get('message', 'Không có thông báo')}")
    print(f"🔍 Lý do: {action_data.get('reasoning', 'Không có')}")
    
    print("\n📝 CODE FINAL:\n")
    print(state_data.get("code", "Không có code được sinh ra"))
    
    # 4. Xuất log ra file JSON để debug chi tiết các trường History
    with open("debug_last_run.json", "w", encoding="utf-8") as f:
        json.dump(final_state, f, ensure_ascii=False, indent=2)
    print("\n[INFO] Đã xuất toàn bộ chi tiết state vào file 'debug_last_run.json'.")

if __name__ == "__main__":
    run_agent("Viết hàm tìm số nguyên tố từ 1 đến n")
    
    # Bạn có thể thử thêm các test case khó hơn, ví dụ: 
    # run_agent("Viết hàm chia hai số a và b")