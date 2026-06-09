from src.nodes.node_3_router import CriticRouter

def _state(**overrides):
  base = {"requirement": "x", "code": "y", "execution_result": {},
          "is_success": False, "retry_count": 0, "max_retries": 3, "history": []}
  base.update(overrides)
  return {"state": base}

def test_success_ends():
  out = CriticRouter()(_state(is_success=True))
  assert out["action"]["next_node"] == "END_SUCCESS"

def test_failure_retries_and_increments():
  out = CriticRouter()(_state(is_success=False, retry_count=1))
  assert out["action"]["next_node"] == "code_generator"
  assert out["state"]["retry_count"] == 2

def test_max_retries_fails():
  out = CriticRouter()(_state(is_success=False, retry_count=3))
  assert out["action"]["next_node"] == "END_FAILURE"
  assert out["state"]["retry_count"] == 3  # unchanged
