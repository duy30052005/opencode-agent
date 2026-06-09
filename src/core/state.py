"""
LangGraph State Definition

Định nghĩa cấu trúc dữ liệu state cho toàn bộ workflow.
State này sẽ được truyền qua các nodes trong LangGraph.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkflowState:
    """
    Trạng thái chính của workflow.
    
    Tương tự như state trong docs/SCHEMA.md nhưng được định nghĩa
    dưới dạng dataclass để LangGraph quản lý dễ hơn.
    """
    
    # ===== METADATA =====
    task_id: str = field(default_factory=lambda: "default_task")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"
    llm_model: str = "gemini-2.5-flash"
    
    # ===== REQUIREMENT =====
    requirement: str = ""
    
    # ===== CODE =====
    code: Optional[str] = None
    
    # ===== EXECUTION RESULT =====
    execution_result: Dict[str, Any] = field(default_factory=dict)
    is_success: bool = False
    
    # ===== RETRY LOGIC =====
    retry_count: int = 0
    max_retries: int = 3
    
    # ===== HISTORY =====
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # ===== ROUTER DECISION =====
    next_node: Optional[str] = None
    message: str = ""
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dict format (để in log, lưu JSON)"""
        return {
            "metadata": {
                "task_id": self.task_id,
                "timestamp": self.timestamp,
                "version": self.version,
                "llm_model": self.llm_model,
            },
            "state": {
                "requirement": self.requirement,
                "code": self.code,
                "execution_result": self.execution_result,
                "is_success": self.is_success,
                "retry_count": self.retry_count,
                "max_retries": self.max_retries,
                "history": self.history,
            },
            "action": {
                "next_node": self.next_node,
                "message": self.message,
                "reasoning": self.reasoning,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Tạo WorkflowState từ dict format"""
        metadata = data.get("metadata", {})
        state = data.get("state", {})
        action = data.get("action", {})
        
        return cls(
            task_id=metadata.get("task_id", "default_task"),
            timestamp=metadata.get("timestamp", datetime.utcnow().isoformat()),
            version=metadata.get("version", "1.0"),
            llm_model=metadata.get("llm_model", "gemini-2.5-flash"),
            requirement=state.get("requirement", ""),
            code=state.get("code"),
            execution_result=state.get("execution_result", {}),
            is_success=state.get("is_success", False),
            retry_count=state.get("retry_count", 0),
            max_retries=state.get("max_retries", 3),
            history=state.get("history", []),
            next_node=action.get("next_node"),
            message=action.get("message", ""),
            reasoning=action.get("reasoning", ""),
        )
