import sys
from pathlib import Path

# Add project root to path FIRST
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from graph.graph import get_graph
import asyncio

load_dotenv()

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a desktop AI agent. "
        "You have access to tools that can interact with the user's computer, "
        "run commands, read/write files, and perform system-level tasks. "
        "You should decide when to use tools and help the user accomplish "
        "whatever they want efficiently and safely. "
        "Use sequential-thinking to reason step by step before complex actions. Store important facts in memory"
    )
)

# Predefined test questions
TEST_QUESTIONS = [
    # "make a folder named joydeep in D drive and init make 3 files named 1.txt , 2.txt , 3.txt and add 3 different jokes in it"
    "list files in my google drive"
    # "What is the current directory?",
    # "Can you list the files in the current directory?",
    # "Create a file named test.txt with the content 'Hello, World!'",
    # "Read the contents of test.txt",
    # "What files did we create during this conversation?",
]


async def main():
    chatbot = await get_graph()
    print("=" * 60)
    print("Starting Chatbot Test with Predefined Questions")
    print("=" * 60)
    print()
    
    thread_id = "test-thread"
    initialized = False
    
    for idx, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'=' * 60}")
        print(f"Question {idx}/{len(TEST_QUESTIONS)}: {question}")
        print('=' * 60)
        
        if not initialized:
            messages = [
                SYSTEM_PROMPT,
                HumanMessage(content=question),
            ]
            initialized = True
        else:
            messages = [HumanMessage(content=question)]
        
        state = {"messages": messages}
        
        try:
            result = await chatbot.ainvoke(
                state,
                config={"configurable": {"thread_id": thread_id}},
            )
            
            response = result["messages"][-1].content
            print(f"\nBot: {response}")
            
        except Exception as e:
            print(f"\nError processing question: {str(e)}")
            print(f"Error type: {type(e).__name__}")
        
        # Optional: Add a small delay between questions
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())