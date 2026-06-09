"""
LangGraph Graph Definition

Tệp này kết nối 3 nodes thành một workflow sử dụng LangGraph.
Bạn có thể quản lý luồng hoạt động của workflow ở đây.
"""

from typing import Any, Dict, Union
from langgraph.graph import StateGraph, END
from langgraph.types import StateSnapshot

from .state import WorkflowState
from ..nodes.node_1_generator import CodeGenerator
from ..nodes.node_2_executor import CodeExecutor
from ..nodes.node_3_router import CriticRouter


# ===== KHỞI TẠO NODES =====
code_generator = CodeGenerator()
code_executor = CodeExecutor()
critic_router = CriticRouter()


# ===== WRAPPER FUNCTIONS (để LangGraph gọi) =====

def node_1_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Code Generator
    
    Input: WorkflowState dict
    Output: WorkflowState dict cập nhật
    """
    # Chuyển dict → WorkflowState
    workflow_state = WorkflowState.from_dict(state)
    
    # Gọi node
    result = code_generator(state)
    
    # Chuyển kết quả → dict format
    output_state = WorkflowState.from_dict(result)
    
    print(f"✅ Node 1 (Generator) hoàn thành")
    print(f"   Message: {output_state.message}")
    print(f"   Next: {output_state.next_node}\n")
    
    return output_state.to_dict()


def node_2_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Code Executor
    
    Input: WorkflowState dict
    Output: WorkflowState dict cập nhật
    """
    workflow_state = WorkflowState.from_dict(state)
    
    result = code_executor(state)
    
    output_state = WorkflowState.from_dict(result)
    
    print(f"⚡ Node 2 (Executor) hoàn thành")
    print(f"   Status: {'✅ Success' if output_state.is_success else '❌ Failed'}")
    print(f"   Message: {output_state.message}")
    print(f"   Next: {output_state.next_node}\n")
    
    return output_state.to_dict()


def node_3_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Critic/Router
    
    Input: WorkflowState dict
    Output: WorkflowState dict cập nhật (+ quyết định retry hoặc END)
    """
    workflow_state = WorkflowState.from_dict(state)
    
    result = critic_router(state)
    
    output_state = WorkflowState.from_dict(result)
    
    print(f"🔍 Node 3 (Router) hoàn thành")
    print(f"   Decision: {output_state.next_node}")
    print(f"   Message: {output_state.message}")
    print(f"   Retry Count: {output_state.retry_count}/{output_state.max_retries}\n")
    
    return output_state.to_dict()


# ===== ROUTER LOGIC (quyết định node tiếp theo) =====

def route_after_node_3(state: Dict[str, Any]) -> str:
    """
    Sau Node 3, quyết định:
    - Quay lại Node 1 (retry)
    - Kết thúc thành công
    - Kết thúc thất bại
    """
    workflow_state = WorkflowState.from_dict(state)
    next_node = workflow_state.next_node
    
    if next_node == "code_generator":
        return "node_1_generator"  # Retry
    elif next_node == "END_SUCCESS":
        return END
    elif next_node == "END_FAILURE":
        return END
    else:
        return END


# ===== BUILD LANGGRAPH =====

def build_workflow_graph():
    """
    Tạo LangGraph workflow.
    
    Flow:
    Node 1 (Generator) 
        → Node 2 (Executor)
            → Node 3 (Router)
                → [Retry → Node 1 | Success → END | Failure → END]
    """
    
    # Tạo StateGraph (LangGraph)
    workflow = StateGraph(WorkflowState)
    
    # ===== THÊM NODES =====
    workflow.add_node("node_1_generator", node_1_wrapper)
    workflow.add_node("node_2_executor", node_2_wrapper)
    workflow.add_node("node_3_router", node_3_wrapper)
    
    # ===== THÊM EDGES (KẾT NỐI NODES) =====
    
    # Entry point: Node 1
    workflow.set_entry_point("node_1_generator")
    
    # Node 1 → Node 2 (luôn)
    workflow.add_edge("node_1_generator", "node_2_executor")
    
    # Node 2 → Node 3 (luôn)
    workflow.add_edge("node_2_executor", "node_3_router")
    
    # Node 3 → [Retry | Success | Failure]
    workflow.add_conditional_edges(
        "node_3_router",
        route_after_node_3,
        {
            "node_1_generator": "node_1_generator",  # Retry path
            END: END,  # Success or Failure path
        }
    )
    
    # Compile workflow
    return workflow.compile()


# ===== PUBLIC API =====

def get_graph():
    """
    Lấy compiled graph object.
    
    Dùng để:
    - Chạy workflow: graph.invoke(initial_state)
    - Visualize: graph.get_graph().draw_mermaid_png()
    - Debug: xem cấu trúc graph
    """
    return build_workflow_graph()


def visualize_graph():
    """
    In ra hình ảnh của graph (Mermaid format).
    
    Dùng để debug workflow structure.
    """
    graph = get_graph()
    try:
        print(graph.get_graph().draw_mermaid())
    except Exception as e:
        print(f"Cannot visualize graph: {e}")


# ===== UTILITIES =====

def get_graph_structure():
    """
    Lấy thông tin cấu trúc của graph (debug).
    """
    graph = get_graph()
    return {
        "nodes": list(graph.get_graph().nodes.keys()),
        "edges": [
            (str(edge[0]), str(edge[1]), edge[2].get("label", ""))
            for edge in graph.get_graph().edges
        ]
    }
