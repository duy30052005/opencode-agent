from typing import TypedDict
from enum import Enum

class Status(Enum, str):
    ERROR = "error"
    SUCCESS = "success"
    PENDING = "pending"
    TIMEOUT = "timeout"

class NodeType(Enum, str):
    GENERATOR = "code_generator"
    EXECUTOR = "code_executor"
    ROUTER = "critic_router"

class TestCase(TypedDict):
    input: str | dict
    expected_output: str | dict
    actual_output: str | dict
    passed: bool

class ExecutionResult(TypedDict):
    status: Status
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms :int
    test_cases: list[TestCase]

class HistoryEntry(TypedDict):
    attempt: int
    node: NodeType
    input: dict
    output: dict
    timestamp: str
    duration_ms: int

class Metadata(TypedDict):
    task_id: str
    timestamp: str
    version: str
    llm_model: str

class State(TypedDict):
    requirement: str
    code: str | None
    execution_result: ExecutionResult
    is_success: bool
    retry_count: int
    max_retries: int
    history: list[HistoryEntry]

class Action(TypedDict):
    next_node: str
    message: str
    reasoning: str

class AgentState(TypedDict):
    metadata: Metadata
    state: State
    action: Action | None