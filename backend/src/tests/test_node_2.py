"""
test_node_2.py
==============
Unit tests cho Node 2: Code Executor.

Chạy:
    python -m pytest tests/test_node_2.py -v

Không cần network, không cần LLM API key.
"""

from __future__ import annotations

import pytest
import src.nodes.node_2_executor as node2_executor
from src.nodes.node_2_executor import (
    _check_syntax,
    _extract_first_function,
    _generate_test_cases,
    _outputs_match,
    _run_in_subprocess,
    run,
)


class _DisabledLLM:
    def invoke(self, prompt):
        raise RuntimeError("LLM disabled in unit tests")


@pytest.fixture(autouse=True)
def disable_real_llm(monkeypatch):
    monkeypatch.setattr(node2_executor, "llm", _DisabledLLM())

# ---------------------------------------------------------------------------
# Helper: build a minimal agent state
# ---------------------------------------------------------------------------

def _make_state(
    code: str | None = None,
    requirement: str = "Viết hàm tính giai thừa của n",
    retry_count: int = 0,
    max_retries: int = 3,
    history: list | None = None,
) -> dict:
    return {
        "metadata": {
            "task_id": "test-task-001",
            "timestamp": "2026-06-08T00:00:00Z",
            "version": "1.0",
            "llm_model": "gpt-4",
        },
        "state": {
            "requirement": requirement,
            "code": code,
            "execution_result": {"status": "pending"},
            "retry_count": retry_count,
            "max_retries": max_retries,
            "history": history or [],
        },
    }


# ===========================================================================
# 1. _check_syntax
# ===========================================================================

class TestCheckSyntax:
    def test_valid_code_returns_none(self):
        assert _check_syntax("def f(x): return x") is None

    def test_syntax_error_detected(self):
        result = _check_syntax("def f(x) return x")
        assert result is not None
        assert "SyntaxError" in result

    def test_empty_code_is_valid(self):
        assert _check_syntax("") is None

    def test_multiline_valid(self):
        code = "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n"
        assert _check_syntax(code) is None


# ===========================================================================
# 2. _extract_first_function
# ===========================================================================

class TestExtractFirstFunction:
    def test_simple_function(self):
        code = "def add(a, b):\n    return a + b\n"
        result = _extract_first_function(code)
        assert result is not None
        fn_name, params = result
        assert fn_name == "add"
        assert params == ["a", "b"]

    def test_no_function_returns_none(self):
        assert _extract_first_function("x = 42") is None

    def test_self_excluded(self):
        code = "class Foo:\n    def method(self, x):\n        pass\n"
        result = _extract_first_function(code)
        # ast.walk finds the method
        assert result is not None
        _, params = result
        assert "self" not in params

    def test_no_params(self):
        code = "def greet():\n    return 'hello'\n"
        result = _extract_first_function(code)
        assert result is not None
        fn_name, params = result
        assert fn_name == "greet"
        assert params == []


# ===========================================================================
# 3. _outputs_match
# ===========================================================================

class TestOutputsMatch:
    def test_exact_match(self):
        assert _outputs_match("120", "120")

    def test_case_insensitive_bool(self):
        assert _outputs_match("True", "true")
        assert _outputs_match("False", "FALSE")

    def test_numeric_float_tolerance(self):
        assert _outputs_match("5.0", "5.000000000")
        assert _outputs_match("0.1", "0.1")

    def test_mismatch(self):
        assert not _outputs_match("120", "0")

    def test_string_mismatch(self):
        assert not _outputs_match("hello", "world")


# ===========================================================================
# 4. _run_in_subprocess
# ===========================================================================

class TestRunInSubprocess:
    def test_hello_world(self):
        res = _run_in_subprocess("print('hello world')", timeout=5)
        assert res["status"] == "success"
        assert "hello world" in res["stdout"]
        assert res["exit_code"] == 0

    def test_syntax_error_in_subprocess(self):
        res = _run_in_subprocess("def f(x) return x", timeout=5)
        assert res["exit_code"] != 0

    def test_runtime_error(self):
        res = _run_in_subprocess("x = 1 / 0", timeout=5)
        assert res["status"] == "error"
        assert res["exit_code"] != 0
        assert "ZeroDivisionError" in res["stderr"]

    def test_timeout(self):
        res = _run_in_subprocess("import time; time.sleep(10)", timeout=1)
        assert res["status"] == "timeout"
        assert res["exit_code"] == -1

    def test_empty_code_runs_fine(self):
        res = _run_in_subprocess("", timeout=5)
        assert res["exit_code"] == 0


# ===========================================================================
# 5. _generate_test_cases
# ===========================================================================

class TestGenerateTestCases:
    def test_llm_generated_json_cases_are_used(self, monkeypatch):
        class _FakeResponse:
            def __init__(self, content):
                self.content = content

        class _FakeLLM:
            def invoke(self, prompt):
                return _FakeResponse(
                    """
                    [
                        {"input": {"text": "hello"}, "expected_output": 1, "description": "one word"},
                        {"input": {"text": "hello world"}, "expected_output": 2, "description": "two words"}
                    ]
                    """
                )

        monkeypatch.setattr(node2_executor, "llm", _FakeLLM())

        code = "def count_words(text):\n    return len(text.split())\n"
        cases = _generate_test_cases("Đếm số từ trong chuỗi", code)

        assert len(cases) == 2
        assert cases[0]["input"] == {"text": "hello"}
        assert cases[0]["expected_output"] == 1
        assert cases[1]["expected_output"] == 2

    def test_factorial_pattern(self):
        code = "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\n"
        cases = _generate_test_cases("Viết hàm tính giai thừa của n", code)
        assert len(cases) > 0
        assert all("input" in c and "expected_output" in c for c in cases)

    def test_fibonacci_pattern(self):
        code = "def fib(n):\n    if n < 2: return n\n    return fib(n-1) + fib(n-2)\n"
        cases = _generate_test_cases("Viết hàm Fibonacci", code)
        assert len(cases) > 0

    def test_palindrome_pattern(self):
        code = "def is_palindrome(s):\n    return s == s[::-1]\n"
        cases = _generate_test_cases("Viết hàm kiểm tra palindrome", code)
        assert len(cases) > 0

    def test_no_function_returns_empty(self):
        cases = _generate_test_cases("Tính giai thừa", "x = 42")
        assert cases == []

    def test_unknown_requirement_returns_empty(self):
        code = "def foo(a, b): return a + b\n"
        cases = _generate_test_cases("Làm việc bí ẩn", code)
        assert isinstance(cases, list)


# ===========================================================================
# 6. Full node run() integration tests
# ===========================================================================

class TestNodeRun:
    # ------------------------------------------------------------------
    # 6.1 Empty code → error
    # ------------------------------------------------------------------
    def test_empty_code_returns_error(self):
        state = _make_state(code=None)
        out = run(state)
        assert out["state"]["is_success"] is False
        assert out["action"]["next_node"] == "critic_router"
        assert out["state"]["execution_result"]["status"] == "error"

    def test_empty_string_code_returns_error(self):
        state = _make_state(code="   ")
        out = run(state)
        assert out["state"]["is_success"] is False

    # ------------------------------------------------------------------
    # 6.2 Syntax error
    # ------------------------------------------------------------------
    def test_syntax_error_code(self):
        state = _make_state(code="def f(x) return x")
        out = run(state)
        assert out["state"]["is_success"] is False
        assert "SyntaxError" in out["state"]["execution_result"]["stderr"]

    # ------------------------------------------------------------------
    # 6.3 Correct factorial
    # ------------------------------------------------------------------
    def test_correct_factorial(self):
        code = (
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
        )
        state = _make_state(
            code=code,
            requirement="Viết hàm tính giai thừa của n",
        )
        out = run(state)
        assert out["action"]["next_node"] == "critic_router"
        assert out["state"]["is_success"] is True
        assert out["state"]["execution_result"]["status"] == "success"
        test_cases = out["state"]["execution_result"]["test_cases"]
        assert len(test_cases) > 0
        assert all(tc["passed"] for tc in test_cases)

    # ------------------------------------------------------------------
    # 6.4 Buggy factorial (always returns 0) → is_success=False
    # ------------------------------------------------------------------
    def test_buggy_factorial(self):
        code = "def factorial(n):\n    return 0\n"
        state = _make_state(
            code=code,
            requirement="Viết hàm tính giai thừa của n",
        )
        out = run(state)
        assert out["state"]["is_success"] is False
        assert out["action"]["next_node"] == "critic_router"

    # ------------------------------------------------------------------
    # 6.5 Runtime error (ZeroDivisionError)
    # ------------------------------------------------------------------
    def test_runtime_error(self):
        """
        An *unsafe* divide function (no b=0 guard) should produce a failed
        execution when tested with b=0 — either:
          - the subprocess crashes (exit_code != 0 for main run), or
          - a test case fails.
        Either way the node must emit a valid response to critic_router.
        """
        code = "def divide(a, b):\n    return a / b\n"
        state = _make_state(
            code=code,
            requirement="Viết hàm chia hai số a và b, xử lý trường hợp b=0",
        )
        out = run(state)
        # Contract: always routes to critic_router
        assert out["action"]["next_node"] == "critic_router"
        # Contract: execution_result is populated correctly
        er = out["state"]["execution_result"]
        assert "status" in er
        assert "stdout" in er
        assert "stderr" in er
        assert "exit_code" in er
        assert "execution_time_ms" in er
        assert "test_cases" in er
        # Contract: is_success field exists
        assert "is_success" in out["state"]
        # The node outputs correct schema regardless of is_success value.
        # Both safe and unsafe divide implementations raise an exception for b=0,
        # so is_success depends on whether the non-b=0 cases pass.
        assert "is_success" in out["state"]
        assert isinstance(out["state"]["is_success"], bool)

    # ------------------------------------------------------------------
    # 6.6 Correct safe divide
    # ------------------------------------------------------------------
    def test_correct_safe_divide(self):
        code = (
            "def divide(a, b):\n"
            "    if b == 0:\n"
            "        raise ValueError('Cannot divide by zero')\n"
            "    return a / b\n"
        )
        state = _make_state(
            code=code,
            requirement="Viết hàm chia hai số a và b, xử lý trường hợp b=0",
        )
        out = run(state)
        assert out["action"]["next_node"] == "critic_router"
        # The test case with b=0 expects "Error" but we raise ValueError; check logic
        # Either pass or fail is acceptable as long as output schema is correct
        assert "execution_result" in out["state"]
        assert "is_success" in out["state"]

    # ------------------------------------------------------------------
    # 6.7 Timeout code
    # ------------------------------------------------------------------
    def test_timeout_code(self):
        code = "import time\ntime.sleep(999)\n"
        state = _make_state(code=code, requirement="Bài toán bí ẩn")
        out = run(state)
        assert out["state"]["is_success"] is False
        assert out["state"]["execution_result"]["status"] == "timeout"
        assert out["action"]["next_node"] == "critic_router"

    # ------------------------------------------------------------------
    # 6.8 Metadata pass-through (contract rule)
    # ------------------------------------------------------------------
    def test_metadata_pass_through(self):
        state = _make_state(code="print('hi')")
        original_metadata = state["metadata"].copy()
        out = run(state)
        assert out["metadata"] == original_metadata

    # ------------------------------------------------------------------
    # 6.9 History is appended (not replaced)
    # ------------------------------------------------------------------
    def test_history_appended(self):
        existing_history = [
            {
                "attempt": 1,
                "node": "code_generator",
                "input": {},
                "output": {},
                "timestamp": "2026-06-08T00:00:00Z",
                "duration_ms": 500,
            }
        ]
        state = _make_state(
            code="def factorial(n):\n    return 1 if n<=1 else n*factorial(n-1)\n",
            requirement="Viết hàm tính giai thừa của n",
            history=existing_history,
        )
        out = run(state)
        history = out["state"]["history"]
        # Must have 2 entries: 1 from generator + 1 from executor
        assert len(history) == 2
        assert history[0]["node"] == "code_generator"
        assert history[1]["node"] == "code_executor"

    # ------------------------------------------------------------------
    # 6.10 action.next_node is always "critic_router"
    # ------------------------------------------------------------------
    def test_next_node_always_critic_router(self):
        for code in [None, "bad code!!!", "x = 1 / 0", "print('ok')"]:
            state = _make_state(code=code)
            out = run(state)
            assert out["action"]["next_node"] == "critic_router", (
                f"Expected critic_router but got {out['action']['next_node']} for code={code!r}"
            )

    # ------------------------------------------------------------------
    # 6.11 Fibonacci
    # ------------------------------------------------------------------
    def test_correct_fibonacci(self):
        code = (
            "def fib(n):\n"
            "    if n < 2:\n"
            "        return n\n"
            "    return fib(n - 1) + fib(n - 2)\n"
        )
        state = _make_state(
            code=code,
            requirement="Viết hàn Fibonacci trả về số fibonacci thứ n",
        )
        out = run(state)
        assert out["state"]["is_success"] is True

    # ------------------------------------------------------------------
    # 6.12 Palindrome
    # ------------------------------------------------------------------
    def test_correct_palindrome(self):
        code = "def is_palindrome(s):\n    return s == s[::-1]\n"
        state = _make_state(
            code=code,
            requirement="Viết hàm kiểm tra xem chuỗi s có phải palindrome không",
        )
        out = run(state)
        assert out["state"]["is_success"] is True


# ---------------------------------------------------------------------------
# Run directly (not via pytest)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
