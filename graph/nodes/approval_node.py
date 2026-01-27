from graph.state import ChatState

async def approval_node(state: ChatState):
    """Ask user for approval before executing tools."""
    #No need of approval
    # return {"approved": True}
    
    last_message = state["messages"][-1]
    
    # Check if there are tool calls to approve
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("\n The AI wants to use the following tools:")
        for tool_call in last_message.tool_calls:
            print(f"  - {tool_call['name']}")
        
        while True:
            approval = input("\nApprove tool execution? (yes/no): ").lower().strip()
            if approval in {'yes', 'y'}:
                return {"approved": True}
            elif approval in {'no', 'n'}:
                return {"approved": False}
            else:
    
                print("Please answer 'yes' or 'no'")
    
    # No tool calls, continue normally
    return {"approved": True}