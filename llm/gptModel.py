import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from graph.tools.tools import get_tools

load_dotenv()

async def get_gptModel():
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
    
    # Try these models in order
    models_to_try = [
        "gpt-4o-mini",      
    ]
    
    for model_id in models_to_try:
        try:
            print(f"Trying model: {model_id}")
            
            chat_model = ChatOpenAI(
                model=model_id,
                api_key=api_key,
                temperature=0.1,

            )
            
            # Test the connection with a simple call
            chat_model.invoke("test")
            
            print(f"✓ Successfully initialized {model_id}")
            
            tools =await get_tools()
            # print(tools)
            chat_model_with_tools = chat_model.bind_tools(tools)
            return chat_model_with_tools
            
        except Exception as e:
            print(f"✗ Failed with {model_id}: {e}")
            continue
    
    raise RuntimeError("All model initialization attempts failed")
