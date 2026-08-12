from src.delivery import orchestrator
from src.delivery.approval import request_approval

def test_protected_branch_blocks():
      ok = {"findings":[{"category":"syntax","severity":"ok","comment":"x"}],"passed":True,"summary":""}
      assert request_approval(ok, "diff", "main") is False        # no Docker, no prompt

def test_push_blocked_keeps_mcp_unused(monkeypatch):
      called = {"n": 0}
      monkeypatch.setattr(orchestrator.mcp_client, "deliver_via_mcp",
                          lambda **k: called.__setitem__("n", called["n"]+1))
      # critical review -> deliver() must return False and never call MCP
      monkeypatch.setattr(orchestrator, "run_ai_review",
          lambda c, r: {"findings":[{"category":"security","severity":"critical","comment":"x"}],
                        "passed": False, "summary": ""})
      assert orchestrator.deliver("code", "req", target_branch="feature/x") is False
      assert called["n"] == 0          # MCP never touched when blocked
def test_happy_path_delivers_in_order(monkeypatch):
      events = []
      calls = {"n": 0, "kwargs": None}

      # 1. review passes
      monkeypatch.setattr(orchestrator, "run_ai_review",
          lambda c, r: {"findings": [{"category": "syntax", "severity": "ok", "comment": "x"}],
                        "passed": True, "summary": ""})
      # 2. human approves (skip the interactive Prompt.ask)
      monkeypatch.setattr(orchestrator, "request_approval", lambda report, diff, branch: True)
      # 3. never touch GitHub auth / device flow
      monkeypatch.setattr(orchestrator.auth, "get_user_token", lambda: "fake-token")
      # 4. capture the MCP delivery instead of spawning Docker
      def fake_deliver(**kwargs):
          calls["n"] += 1
          calls["kwargs"] = kwargs
          return "https://github.com/o/r/pull/1"
      monkeypatch.setattr(orchestrator.mcp_client, "deliver_via_mcp", fake_deliver)
      # 5. capture audit events (don't append to the real jsonl file)
      monkeypatch.setattr(orchestrator.audit, "log_event",
          lambda action, **k: events.append(action))

      ok = orchestrator.deliver("def add(a, b): return a + b", "add two numbers",
                                target_branch="feature/x", filename="solution.py")

      assert ok is True
      assert calls["n"] == 1                          # MCP called exactly once
      assert calls["kwargs"]["branch"] == "feature/x" # right branch...
      assert calls["kwargs"]["path"] == "solution.py" # ...and file threaded through
      assert events == ["review", "push"]             # ordering, and 'blocked' never logged

def test_review_ok_but_no_approval_skips_push(monkeypatch):
      called = {"n": 0}
      # review passes...
      monkeypatch.setattr(orchestrator, "run_ai_review",
          lambda c, r: {"findings": [{"category": "syntax", "severity": "ok", "comment": "x"}],
                        "passed": True, "summary": ""})
      # ...but the human declines (types anything other than APPROVED)
      monkeypatch.setattr(orchestrator, "request_approval", lambda report, diff, branch: False)
      monkeypatch.setattr(orchestrator.mcp_client, "deliver_via_mcp",
                          lambda **k: called.__setitem__("n", called["n"] + 1))
      assert orchestrator.deliver("code", "req", target_branch="feature/x") is False
      assert called["n"] == 0          # no approval -> MCP never called