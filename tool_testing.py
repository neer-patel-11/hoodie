from graph.tools.fileSystem import list_directory 
from graph.tools.processManager import list_processes , find_process_by_name

# Test file operations
result = list_directory.invoke({"path": "C:"})
print(result)

# Test process operations
print(list_processes.invoke({"limit":10,"sort_by": "memory"}))
print(find_process_by_name.invoke({"name":"chrome"}))