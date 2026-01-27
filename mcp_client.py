from langchain_mcp_adapters.client import MultiServerMCPClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MultiServerMCPClient(
     {
        "filesystem": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "@modelcontextprotocol/server-filesystem",
                "D:/",
            ],
        }, 

        # Browser automation with Playwright
        "playwright": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "@executeautomation/playwright-mcp-server"
            ],
            "env": {
                "PLAYWRIGHT_HEADLESS": "false",
                "PLAYWRIGHT_KEEP_OPEN": "true",  # If supported
                "PLAYWRIGHT_TIMEOUT": "0"    # 5 minutes timeout
            }
        },

        # Memory/context storage
        "memory": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "@modelcontextprotocol/server-memory"
            ],
        },
        
    #     # Sequential thinking for complex tasks
        "sequential-thinking": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "@modelcontextprotocol/server-sequential-thinking"
            ],
        },
        
        
        "github": {
            "transport": "stdio",
            "command": "python",
            "args": ["D:\AI_agents\hodie\mcp_server\github_mcp_server.py"],
            "env": {
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
            }
        },

        
        "google-drive": {
        "transport": "stdio",
        "command": "python",
        "args": ["D:\AI_agents\hodie\mcp_server\google_drive_mcp_server.py"]
        }
    
    }
    
)


async def get_mcp_tools():
    return await client.get_tools()
