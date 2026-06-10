"""
LangGraph Workflow Definition
Kết nối 3 nodes thành một vòng lặp: Generator -> Executor -> Router
"""

from typing import Any, Dict
from langgraph.graph import StateGraph, END

# Import schemas chuẩn của dự án
from ..schemas.agent_state import AgentState

# Import 3 nodes do Vinh, Bằng, Mẫn phụ trách
from ..nodes.node_1_generator import CodeGenerator
from ..nodes.node_2_executor import CodeExecutor
from ..nodes.node_3_router import CriticRouter

def create_workflow():
    # 1. Khởi tạo StateGraph với AgentState TypedDict
    workflow = StateGraph(AgentState)

    # 2. Khởi tạo các Node instances
    node_1 = CodeGenerator()
    node_2 = CodeExecutor()
    node_3 = CriticRouter()

    # 3. Wrapper functions để in log cho dễ theo dõi tiến trình
    def run_node_1(state: AgentState) -> AgentState:
        print("\n[Node 1 - Vinh] Đang đọc requirement và sinh code...")
        return node_1(state)

    def run_node_2(state: AgentState) -> AgentState:
        print("\n[Node 2 - Bằng] Đang thực thi code trong môi trường an toàn...")
        return node_2(state)

    def run_node_3(state: AgentState) -> AgentState:
        print("\n[Node 3 - Mẫn] Đang đánh giá kết quả thực thi...")
        return node_3(state)

    # 4. Định nghĩa Router Logic (Đọc quyết định từ Node 3)
    def route_after_critic(state: AgentState) -> str:
        action = state.get("action")
        if not action:
            return END
            
        next_node = action.get("next_node")
        if next_node == "code_generator":
            retry = state.get("state", {}).get("retry_count", 0)
            print(f"🔄 QUYẾT ĐỊNH: Code có lỗi. Quay lại Node 1 (Lần thử {retry + 1})")
            return "node_1_generator"
        elif next_node == "END_SUCCESS":
            print("🏁 QUYẾT ĐỊNH: Tất cả test case PASS. Kết thúc thành công!")
            return END
        else:
            print("🛑 QUYẾT ĐỊNH: Đã hết số lần thử hoặc lỗi nghiêm trọng. Dừng hệ thống.")
            return END

    # 5. Đăng ký các Nodes vào đồ thị
    workflow.add_node("node_1_generator", run_node_1)
    workflow.add_node("node_2_executor", run_node_2)
    workflow.add_node("node_3_router", run_node_3)

    # 6. Thiết lập điểm bắt đầu
    workflow.set_entry_point("node_1_generator")

    # 7. Kết nối các Nodes (Edges)
    workflow.add_edge("node_1_generator", "node_2_executor")
    workflow.add_edge("node_2_executor", "node_3_router")
    
    # Tại Node 3, dùng Conditional Edges để điều hướng
    workflow.add_conditional_edges(
        "node_3_router",
        route_after_critic,
        {
            "node_1_generator": "node_1_generator",
            END: END
        }
    )

    # Biên dịch đồ thị
    return workflow.compile()

# Khởi tạo sẵn một instance để các file khác dễ dàng import và gọi `.invoke()`
app = create_workflow()