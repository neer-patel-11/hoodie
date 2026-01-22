import asyncio
from mcpConfig.loader import MCPToolLoader

_loader = MCPToolLoader("mcpConfig/config.yaml")

def get_mcp_tools():
    """Sync wrapper for LangGraph"""
    return asyncio.run(_loader.load_tools())
