from typing import TypedDict
from .agent_state import Action, State

class Node3Input(TypedDict):
  state: State
  action: Action
class Node3Output(TypedDict):
  state: State
  action: Action