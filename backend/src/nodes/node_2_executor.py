from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .base_node import BaseNode
from ..core.llm_client import llm
from ..schemas.node_1_schema import Node1Input, Node1Output

TIMEOUT_SECONDS: float = 5.0
MAX_OUTPUT_CHARS: int = 8_000


class CodeExecutor(BaseNode):
    NODE_NAME = "code_executor"

    def __call__(self, state: Node1Input) -> Node1Output:
        node_start = time.time()

        metadata = state.get("metadata", {})
        inner = state.get("state", {})

        code: Optional[str] = inner.get("code")
        requirement: str = inner.get("requirement", "")
        retry_count: int = int(inner.get("retry_count", 0) or 0)
        execution_result_context: Dict[str, Any] = inner.get("execution_result", {}) or {}
        history: List[Dict[str, Any]] = list(inner.get("history", []))

        attempt_number = len(history) + 1

        if not code or not code.strip():
            execution_result = _build_execution_result(
                status="error",
                stdout="",
                stderr="Node 2 received empty code from Node 1.",
                exit_code=1,
                execution_time_ms=0,
                test_cases=[],
            )
            return _build_output(
                metadata=metadata,
                inner=inner,
                execution_result=execution_result,
                is_success=False,
                history=history,
                attempt_number=attempt_number,
                node_start=node_start,
                message="❌ Code rỗng, không thể thực thi!",
                reasoning="code field is empty",
            )

        syntax_error = _check_syntax(code)
        if syntax_error:
            execution_result = _build_execution_result(
                status="error",
                stdout="",
                stderr=syntax_error,
                exit_code=1,
                execution_time_ms=int((time.time() - node_start) * 1000),
                test_cases=[],
            )
            return _build_output(
                metadata=metadata,
                inner=inner,
                execution_result=execution_result,
                is_success=False,
                history=history,
                attempt_number=attempt_number,
                node_start=node_start,
                message="❌ Code có lỗi cú pháp (SyntaxError)!",
                reasoning=f"SyntaxError: {syntax_error}",
            )

        test_cases = _generate_test_cases(
            requirement,
            code,
            retry_count=retry_count,
            execution_result=execution_result_context,
        )
        exec_result = _run_in_subprocess(code, timeout=TIMEOUT_SECONDS)

        evaluated_tests: List[Dict[str, Any]] = []
        if test_cases:
            evaluated_tests = _evaluate_test_cases(code, test_cases, timeout=TIMEOUT_SECONDS)
            all_passed = all(tc["passed"] for tc in evaluated_tests)
            combined_stderr = exec_result["stderr"]
            final_status = "success" if all_passed else "error"
        else:
            all_passed = exec_result["exit_code"] == 0
            combined_stderr = exec_result["stderr"]
            final_status = exec_result["status"]

        execution_result = _build_execution_result(
            status=final_status,
            stdout=exec_result["stdout"],
            stderr=combined_stderr,
            exit_code=exec_result["exit_code"],
            execution_time_ms=exec_result["execution_time_ms"],
            test_cases=evaluated_tests,
        )

        is_success = all_passed and exec_result["exit_code"] == 0

        if is_success:
            message = "✅ Code chạy thành công!"
            reasoning = "Không có lỗi, tất cả test case pass"
        else:
            failed = sum(1 for tc in evaluated_tests if not tc.get("passed", True))
            if exec_result["status"] == "timeout":
                message = "⏱️ Code bị timeout (vượt quá 5 giây)!"
                reasoning = f"Execution timeout after {TIMEOUT_SECONDS}s"
            elif failed:
                message = f"❌ Code bị lỗi! {failed}/{len(evaluated_tests)} test case thất bại."
                reasoning = f"{failed} test case(s) failed"
            else:
                message = "❌ Code bị lỗi khi thực thi!"
                reasoning = exec_result["stderr"][:200] if exec_result["stderr"] else "Non-zero exit code"

        return _build_output(
            metadata=metadata,
            inner=inner,
            execution_result=execution_result,
            is_success=is_success,
            history=history,
            attempt_number=attempt_number,
            node_start=node_start,
            message=message,
            reasoning=reasoning,
        )


def run(state: Node1Input) -> Node1Output:
    return CodeExecutor()(state)


def _check_syntax(code: str) -> Optional[str]:
    try:
        ast.parse(code)
        return None
    except SyntaxError as exc:
        return f"SyntaxError at line {exc.lineno}: {exc.msg}"


def _run_in_subprocess(
    code: str,
    timeout: float = TIMEOUT_SECONDS,
    stdin_data: Optional[str] = None,
) -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        prefix="node2_exec_",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONIOENCODING": "utf-8",
            },
        )
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        stdout = _truncate(result.stdout)
        stderr = _truncate(result.stderr)
        exit_code = result.returncode
        status = "success" if exit_code == 0 else "error"
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int(timeout * 1000)
        stdout = _truncate(exc.stdout or "")
        stderr = _truncate(exc.stderr or "") or f"TimeoutError: Code exceeded {timeout}s limit."
        exit_code = -1
        status = "timeout"
    except Exception:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        stdout = ""
        stderr = _truncate(traceback.format_exc())
        exit_code = -2
        status = "error"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return {
        "status": status,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "execution_time_ms": elapsed_ms,
    }


def _run_test_snippet_in_subprocess(
    code: str,
    test_snippet: str,
    timeout: float,
) -> Tuple[str, str, int]:
    combined = code.rstrip() + "\n\n" + textwrap.dedent(test_snippet)
    res = _run_in_subprocess(combined, timeout=timeout)
    return res["stdout"], res["stderr"], res["exit_code"]


def _generate_test_cases(
    requirement: str,
    code: str,
    retry_count: int = 0,
    execution_result: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    fn_info = _extract_first_function(code)
    if fn_info is None:
        return []

    fn_name, param_names = fn_info
    llm_cases = _generate_test_cases_with_llm(
        requirement=requirement,
        code=code,
        fn_name=fn_name,
        param_names=param_names,
        retry_count=retry_count,
        execution_result=execution_result or {},
    )
    if llm_cases:
        return _remap_inputs(llm_cases, param_names)[:5]

    return _generate_rule_based_test_cases(requirement, code)


def _generate_test_cases_with_llm(
    requirement: str,
    code: str,
    fn_name: str,
    param_names: List[str],
    retry_count: int,
    execution_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    signature = ", ".join(param_names) if param_names else "no parameters"
    execution_summary = json.dumps(execution_result, ensure_ascii=False, default=str)
    prompt = f"""You are a strict Python test designer.
Generate 2 to 5 test cases for the requirement below.

Requirement:
{requirement}

Function name: {fn_name}
Parameters: {signature}
Code:
```python
{code}
```

Retry count: {retry_count}
Previous execution result JSON:
{execution_summary}

Rules:
- Return ONLY valid JSON.
- Return a JSON array of objects.
- Each object must have: input, expected_output, description.
- input must be a JSON object whose keys match the function parameters.
- expected_output can be a JSON value, or "__EXCEPTION__" if the correct behavior is to raise.
- Prefer boundary, normal, and edge cases.
- Use the previous execution result to avoid repeating obviously weak cases when retry_count > 0.
- Do not include markdown fences, code, or explanations.
"""

    try:
        response = llm.invoke(prompt)
    except Exception:
        return []

    raw_content = getattr(response, "content", response)
    return _parse_test_case_payload(raw_content)


def _parse_test_case_payload(raw_content: Any) -> List[Dict[str, Any]]:
    if not raw_content:
        return []

    text = str(raw_content).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    start_candidates = [idx for idx in (text.find("["), text.find("{")) if idx != -1]
    if not start_candidates:
        return []

    start = min(start_candidates)
    end = max(text.rfind("]"), text.rfind("}"))
    if end < start:
        return []

    json_blob = text[start : end + 1]
    try:
        parsed = json.loads(json_blob)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        for key in ("test_cases", "cases", "items"):
            value = parsed.get(key)
            if isinstance(value, list):
                parsed = value
                break

    if not isinstance(parsed, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        input_data = item.get("input", {})
        if not isinstance(input_data, dict):
            continue
        expected_output = item.get("expected_output", "")
        normalized.append(
            {
                "input": input_data,
                "expected_output": expected_output,
                "description": str(item.get("description", "")).strip(),
            }
        )

    return normalized[:5]


def _generate_rule_based_test_cases(requirement: str, code: str) -> List[Dict[str, Any]]:
    fn_info = _extract_first_function(code)
    if fn_info is None:
        return []

    _, param_names = fn_info
    req_lower = requirement.lower()

    patterns: List[Tuple[str, List[Dict[str, Any]]]] = [
        (
            r"giai\s*th[uừ]a|factorial",
            [
                {"input": {"n": 0}, "expected_output": "1"},
                {"input": {"n": 1}, "expected_output": "1"},
                {"input": {"n": 5}, "expected_output": "120"},
                {"input": {"n": 10}, "expected_output": "3628800"},
            ],
        ),
        (
            r"fibonacci|fib",
            [
                {"input": {"n": 0}, "expected_output": "0"},
                {"input": {"n": 1}, "expected_output": "1"},
                {"input": {"n": 6}, "expected_output": "8"},
                {"input": {"n": 10}, "expected_output": "55"},
            ],
        ),
        (
            r"palindrome|đối xứng",
            [
                {"input": {"s": "racecar"}, "expected_output": "True"},
                {"input": {"s": "hello"}, "expected_output": "False"},
                {"input": {"s": "madam"}, "expected_output": "True"},
                {"input": {"s": "world"}, "expected_output": "False"},
            ],
        ),
        (
            r"t[oổ]ng|sum.*list|sum.*array|sum.*m[aả]ng",
            [
                {"input": {"lst": [1, 2, 3]}, "expected_output": "6"},
                {"input": {"lst": [0]}, "expected_output": "0"},
                {"input": {"lst": [-1, 1]}, "expected_output": "0"},
            ],
        ),
        (
            r"chia|divid",
            [
                {"input": {"a": 10, "b": 2}, "expected_output": "5.0"},
                {"input": {"a": 0, "b": 5}, "expected_output": "0.0"},
                {"input": {"a": 10, "b": 0}, "expected_output": "__EXCEPTION__"},
            ],
        ),
        (
            r"l[uũ]y th[uừ]a|power|exponent",
            [
                {"input": {"base": 2, "exp": 3}, "expected_output": "8"},
                {"input": {"base": 5, "exp": 0}, "expected_output": "1"},
                {"input": {"base": 3, "exp": 2}, "expected_output": "9"},
            ],
        ),
        (
            r"nguy[eê]n t[oố]|prime|is_prime",
            [
                {"input": {"n": 2}, "expected_output": "True"},
                {"input": {"n": 4}, "expected_output": "False"},
                {"input": {"n": 13}, "expected_output": "True"},
                {"input": {"n": 1}, "expected_output": "False"},
            ],
        ),
        (
            r"đảo ngược|reverse.*string|reverse.*str",
            [
                {"input": {"s": "hello"}, "expected_output": "olleh"},
                {"input": {"s": "abc"}, "expected_output": "cba"},
                {"input": {"s": ""}, "expected_output": ""},
            ],
        ),
        (
            r"\bmax\b|\bmin\b",
            [
                {"input": {"lst": [3, 1, 4, 1, 5]}, "expected_output": "5"},
                {"input": {"lst": [-3, -1]}, "expected_output": "-1"},
            ],
        ),
    ]

    for pattern, cases in patterns:
        if re.search(pattern, req_lower):
            return _remap_inputs(cases, param_names)[:5]

    return []


def _remap_inputs(cases: List[Dict[str, Any]], param_names: List[str]) -> List[Dict[str, Any]]:
    if not param_names:
        return cases

    result = []
    for case in cases:
        inp = case.get("input", {})
        if isinstance(inp, dict):
            inp_keys = list(inp.keys())
            if all(k in param_names for k in inp_keys):
                result.append(case)
                continue
            new_inp: Dict[str, Any] = {}
            for i, val in enumerate(inp.values()):
                if i < len(param_names):
                    new_inp[param_names[i]] = val
            result.append({**case, "input": new_inp})
        else:
            result.append(case)
    return result


def _extract_first_function(code: str) -> Optional[Tuple[str, List[str]]]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            params = [arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")]
            return node.name, params
    return None


def _evaluate_test_cases(code: str, test_cases: List[Dict[str, Any]], timeout: float) -> List[Dict[str, Any]]:
    fn_info = _extract_first_function(code)
    if fn_info is None:
        return [{**tc, "actual_output": "N/A", "passed": False} for tc in test_cases]

    fn_name, _ = fn_info
    results: List[Dict[str, Any]] = []

    for tc in test_cases:
        inp: Dict[str, Any] = tc.get("input", {})
        expected = _normalize_expected_output(tc.get("expected_output", ""))

        call_args = ", ".join(f"{k}={repr(v)}" for k, v in inp.items())
        snippet = textwrap.dedent(
            f"""\
            import json as _json

            try:
                _result = {fn_name}({call_args})
                if isinstance(_result, str):
                    print(_result)
                else:
                    try:
                        print(_json.dumps(_result, ensure_ascii=False, sort_keys=True))
                    except TypeError:
                        print(_result)
            except Exception as _e:
                print(f"EXCEPTION:{{type(_e).__name__}}")
            """
        )

        stdout, stderr, exit_code = _run_test_snippet_in_subprocess(
            code, snippet, timeout=max(timeout / max(len(test_cases), 1), 1.0)
        )

        actual = stdout.strip()
        expects_exception = expected == "__EXCEPTION__"
        expects_error = expected == "__EXPECT_ERROR__"

        if expects_exception:
            passed = actual.startswith("EXCEPTION:") and exit_code == 0
            actual_display = actual
        elif expects_error:
            passed = exit_code != 0
            actual_display = f"ERROR: {stderr.strip()[:200]}" if exit_code != 0 else actual
        else:
            passed = (exit_code == 0) and _outputs_match(actual, expected)
            actual_display = actual if exit_code == 0 else f"ERROR: {stderr.strip()[:200]}"

        results.append(
            {
                "input": inp,
                "expected_output": expected,
                "actual_output": actual_display,
                "passed": passed,
            }
        )

    return results


def _outputs_match(actual: str, expected: str) -> bool:
    if not isinstance(expected, str):
        actual_json = _try_json_loads(actual)
        if actual_json is not _JSON_PARSE_FAILED and actual_json == expected:
            return True

    if actual == expected:
        return True

    if not isinstance(expected, str):
        return False

    expected_json = _try_json_loads(expected)
    actual_json = _try_json_loads(actual)
    if expected_json is not _JSON_PARSE_FAILED and actual_json is not _JSON_PARSE_FAILED:
        if actual_json == expected_json:
            return True

    try:
        return abs(float(actual) - float(expected)) < 1e-9
    except (ValueError, TypeError):
        pass
    return actual.lower() == expected.lower()


_JSON_PARSE_FAILED = object()


def _try_json_loads(value: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return _JSON_PARSE_FAILED


def _normalize_expected_output(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if stripped in {"__EXCEPTION__", "__EXPECT_ERROR__"}:
        return stripped

    parsed = _try_json_loads(stripped)
    if parsed is not _JSON_PARSE_FAILED:
        return parsed

    return value


def _build_execution_result(
    status: str,
    stdout: str,
    stderr: str,
    exit_code: int,
    execution_time_ms: int,
    test_cases: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "status": status,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "execution_time_ms": execution_time_ms,
        "test_cases": test_cases,
    }


def _build_output(
    metadata: Dict[str, Any],
    inner: Dict[str, Any],
    execution_result: Dict[str, Any],
    is_success: bool,
    history: List[Dict[str, Any]],
    attempt_number: int,
    node_start: float,
    message: str,
    reasoning: str,
) -> Dict[str, Any]:
    duration_ms = int((time.time() - node_start) * 1000)
    now_iso = datetime.now(timezone.utc).isoformat()

    history_entry: Dict[str, Any] = {
        "attempt": attempt_number,
        "node": "code_executor",
        "input": {
            "code": (inner.get("code") or "")[:500],
            "requirement": inner.get("requirement", ""),
        },
        "output": {
            "execution_result": execution_result,
            "is_success": is_success,
        },
        "timestamp": now_iso,
        "duration_ms": duration_ms,
    }

    updated_history = history + [history_entry]
    updated_state = {
        **inner,
        "execution_result": execution_result,
        "is_success": is_success,
        "history": updated_history,
    }

    return {
        "metadata": metadata,
        "state": updated_state,
        "action": {
            "next_node": "critic_router",
            "message": message,
            "reasoning": reasoning,
        },
    }


def _truncate(text: str, max_chars: int = MAX_OUTPUT_CHARS) -> str:
    if not text:
        return ""
    if len(text) > max_chars:
        return text[:max_chars] + f"\n... [truncated, total {len(text)} chars]"
    return text