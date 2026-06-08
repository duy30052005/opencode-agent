from .agent_state import AgentState

class BaseNode:
    NODE_NAME: str = "base_node"
    
    def __call__(self, state: AgentState) -> AgentState:
        raise NotImplementedError("Subclasses must implement this method.")