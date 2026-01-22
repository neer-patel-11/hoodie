from llm.llm import get_llm
from graph.state import ChatState
from dotenv import load_dotenv


load_dotenv()



llm = get_llm()

def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    

    messages = state["messages"]
    response = llm.invoke(messages)

    
    
    return {"messages": [response]}

