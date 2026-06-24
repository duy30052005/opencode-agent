"""
LangGraph Workflow Definition
Kết nối 3 nodes thành một vòng lặp: Generator -> Executor -> Router
"""
from langgraph.prebuilt import ToolNode

from ..tools.ast_tools import coding_tools

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

    tool_node = ToolNode(coding_tools)

    def run_tool_node(state: AgentState):
        print("\n[ToolNode - Hệ thống] 🛠️ Đang thực thi công cụ hỗ trợ đọc/ghi...")
        return tool_node.invoke(state)
    # 4. Định nghĩa Router Logic cho Node 1 (MỚI)
    def route_after_generator(state: AgentState) -> str:
        # Kiểm tra xem LLM ở Node 1 có yêu cầu gọi tool không
        # (Dựa trên mảng messages chuẩn của LangGraph)
        messages = state.get("messages", [])
        
        if messages and hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
            print("➡️ QUYẾT ĐỊNH: Node 1 cần thêm thông tin. Chuyển sang ToolNode.")
            return "tool_node"
        
        # Nếu không gọi tool (hoặc Vinh chưa code chức năng này), đi tiếp sang Node 2 như cũ
        print("➡️ QUYẾT ĐỊNH: Node 1 đã chốt code. Chuyển sang Node 2 (Executor).")
        return "node_2_executor"

    # Định nghĩa Router Logic cho Node 3 (GIỮ NGUYÊN CODE CỦA BẠN)
    def route_after_critic(state: AgentState) -> str:
        # 1. Nếu không có action (có thể do lỗi từ các node trước), kết thúc đồ thị
        action = state.get("action")
        if not action:
            print("🛑 QUYẾT ĐỊNH: Không tìm thấy action từ Node 3. Dừng hệ thống.")
            return END
            
        next_node = action.get("next_node")
        
        # 2. Xử lý các luồng điều hướng hợp lệ
        if next_node == "code_generator":
            retry = state.get("state", {}).get("retry_count", 0)
            print(f"🔄 QUYẾT ĐỊNH: Code có lỗi. Quay lại Node 1 (Lần thử {retry + 1})")
            return "node_1_generator"
            
        elif next_node == "END_SUCCESS":
            print("🏁 QUYẾT ĐỊNH: Tất cả test case PASS. Kết thúc thành công!")
            return END
            
        elif next_node == "END_FAILURE":
            print("🛑 QUYẾT ĐỊNH: Đã hết số lần thử hoặc lỗi nghiêm trọng. Dừng hệ thống.")
            return END
            
        # 3. LUÔN LUÔN CÓ MỘT TRƯỜNG HỢP MẶC ĐỊNH (Fallback)
        # Nếu next_node trả về một giá trị lạ hoặc None, ép nó dừng lại
        # Đây là dòng sẽ chặn đứng cái lỗi KeyError: None của bạn
        print(f"⚠️ CẢNH BÁO: Nhận được next_node không xác định: {next_node}. Dừng hệ thống.")
        return END

    # 5. Đăng ký các Nodes vào đồ thị (THÊM TOOL NODE)
    workflow.add_node("node_1_generator", run_node_1)
    workflow.add_node("tool_node", run_tool_node) # Node mới
    workflow.add_node("node_2_executor", run_node_2)
    workflow.add_node("node_3_router", run_node_3)

    # 6. Thiết lập điểm bắt đầu
    workflow.set_entry_point("node_1_generator")

    # 7. Kết nối các Nodes (THAY ĐỔI EDGES)
    # XÓA dòng này: workflow.add_edge("node_1_generator", "node_2_executor")
    
    # THÊM Rẽ nhánh từ Node 1:
    workflow.add_conditional_edges(
        "node_1_generator",
        route_after_generator,
        {
            "tool_node": "tool_node",
            "node_2_executor": "node_2_executor"
        }
    )

    # Nếu chạy Tool xong, BẮT BUỘC quay lại Node 1 để LLM đọc kết quả từ Tool
    workflow.add_edge("tool_node", "node_1_generator")
    
    # Nối Node 2 sang Node 3 như cũ
    workflow.add_edge("node_2_executor", "node_3_router")
    
    # Tại Node 3, dùng Conditional Edges (GIỮ NGUYÊN CODE CỦA BẠN)
    workflow.add_conditional_edges(
        "node_3_router",
        route_after_critic,
        {
            "node_1_generator": "node_1_generator",
            END: END
        }
    )

    return workflow.compile()

# Khởi tạo sẵn một instance để các file khác dễ dàng import và gọi `.invoke()`
app = create_workflow()