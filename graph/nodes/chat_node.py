from llm.llm import get_llm
from graph.state import ChatState
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

load_dotenv()

async def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    
    llm = await get_llm()

    messages = state["messages"]
    
    # If user rejected tool use, inform the LLM
    if state.get("approved") == False:
        # Add a message saying tools were rejected
        messages = messages + [
            AIMessage(content="The user rejected the tool execution. I'll answer without using tools If possible otherwise Say sorry.")
        ]
        # Unbind tools temporarily to force a text response
        response = await llm.ainvoke(messages)
    else:
        response = await llm.ainvoke(messages)

    return {"messages": [response], "approved": True}  # Reset approval