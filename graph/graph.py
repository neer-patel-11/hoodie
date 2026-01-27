from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from graph.nodes.chat_node import chat_node
from graph.nodes.approval_node import approval_node
from graph.nodes.routing import route_after_approval
from graph.state import ChatState
from graph.tools.tools import get_tools

async def get_graph():

    tools = await get_tools()

    tool_node = ToolNode(tools)
    
    memory = MemorySaver()

    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("approval", approval_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    # After chat_node, check if tools are needed
    graph.add_conditional_edges(
        "chat_node", 
        tools_condition,
        {
            "tools": "approval",  # If tools needed, go to approval first
            END: END
        }
    )
    
    # After approval, route based on user's decision
    graph.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "tools": "tools",
            "chat_node": "chat_node"
        }
    )
    
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile(checkpointer=memory)

    return chatbot