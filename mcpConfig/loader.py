import yaml
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import Tool

class MCPToolLoader:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.client = MultiServerMCPClient(
            {
                name: {
                    "command": cfg["command"],
                    "args": cfg["args"],
                    "transport": cfg.get("transport", "stdio"),
                }
                for name, cfg in self.config["servers"].items()
            }
        )

    async def load_tools(self) -> list[Tool]:
        """Fetch tools from all MCP servers"""
        tools = await self.client.get_tools()
        return tools
