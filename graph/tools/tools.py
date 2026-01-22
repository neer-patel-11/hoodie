from graph.tools.duckduckgo import duckduckgo_search
from graph.tools.executeCommand import execute_command
from graph.tools.fileSystem import get_file_info , search_files , create_folder , delete_file_or_folder , write_file , read_file , list_directory

from graph.tools.processManager import list_processes , get_process_info , get_system_info , find_process_by_name , list_disk_drives


from graph.tools.mcpToolsRegistery import get_mcp_tools
# Testing
# @tool
# def add_numbers(a: int, b: int) -> int:
#     """Add two numbers and return the result."""
#     print("using adding tool")
#     return a + b


def get_tools():
    tools = [
        # duckduckgo_search,

        execute_command,

        # #file system
        # get_file_info , search_files , create_folder , delete_file_or_folder , write_file , read_file , list_directory,

        # #process management
        # list_processes , get_process_info ,  get_system_info , find_process_by_name , list_disk_drives


        ]
    
    tools.extend(get_mcp_tools())

    return tools