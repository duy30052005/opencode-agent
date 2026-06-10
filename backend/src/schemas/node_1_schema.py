from typing import TypedDict
from .agent_state import Action, State


class Node1Input(TypedDict):
    state: State

class Node1Output(TypedDict):
    state: State
    action: Action