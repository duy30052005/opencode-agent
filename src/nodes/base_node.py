from datetime import datetime, timezone

from ..schemas.agent_state import State

class BaseNode:
    NODE_NAME: str

    def write_history(self, state: dict, input: dict, output: dict, duration_ms: int) -> dict:
        history_entry = {
            "attempt": state.get("retry_count", 0) + 1,
            "node": self.NODE_NAME,
            "input": input,
            "output": output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms
        }

        if "history" not in state["state"]:
            state["state"]["history"] = []
        state["state"]["history"].append(history_entry)

        return history_entry
