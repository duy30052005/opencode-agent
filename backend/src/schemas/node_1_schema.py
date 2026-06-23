from typing import TypedDict
from langchain_core.messages import AnyMessage
from .agent_state import Action, State, Metadata

class Node1Input(TypedDict):
    messages: list[AnyMessage]
    metadata: Metadata
    state: State

class Node1Output(TypedDict):
    messages: list[AnyMessage]
    metadata: Metadata
    state: State
    action: Action