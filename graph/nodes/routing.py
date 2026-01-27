from graph.state import ChatState
from typing import Literal

def route_after_approval(state: ChatState) -> Literal["tools", "chat_node"]:
    """Route to tools if approved, otherwise back to chat."""
    if state.get("approved", False):
        return "tools"
    else:
        return "chat_node"