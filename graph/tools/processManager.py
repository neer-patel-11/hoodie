from langchain_core.tools import tool
import psutil
import platform
from datetime import datetime

# ============================================
# PROCESS MANAGER TOOLS (Cross-platform)
# ============================================

@tool
def list_processes(limit: int = 20, sort_by: str = "memory") -> str:
    """
    List running processes with details.
    
    Args:
        limit: Maximum number of processes to return (default: 20)
        sort_by: Sort by 'memory' or 'cpu' (default: 'memory')
    
    Returns:
        Formatted string with process information
    """
    print(f"Listing top {limit} processes sorted by {sort_by}")
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu': pinfo['cpu_percent'] or 0,
                    'memory': pinfo['memory_percent'] or 0,
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort processes
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        else:
            processes.sort(key=lambda x: x['memory'], reverse=True)
        
        # Limit results
        processes = processes[:limit]
        
        results = []
        for proc in processes:
            results.append(
                f"PID: {proc['pid']} | {proc['name']}\n"
                f"  CPU: {proc['cpu']:.1f}% | Memory: {proc['memory']:.1f}% | Status: {proc['status']}\n"
            )
        
        return f"Top {limit} processes (sorted by {sort_by}):\n\n" + "\n".join(results)
    
    except Exception as e:
        return f"Error listing processes: {str(e)}"


@tool
def get_process_info(pid: int) -> str:
    """
    Get detailed information about a specific process.
    
    Args:
        pid: Process ID to get information about
    
    Returns:
        Detailed process information
    """
    print(f"Getting info for process PID: {pid}")
    try:
        proc = psutil.Process(pid)
        
        info = [
            f"Process Information (PID: {pid})",
            f"Name: {proc.name()}",
            f"Status: {proc.status()}",
            f"CPU: {proc.cpu_percent(interval=0.1):.1f}%",
            f"Memory: {proc.memory_percent():.1f}%",
            f"Memory (RSS): {proc.memory_info().rss / 1024 / 1024:.1f} MB",
            f"Threads: {proc.num_threads()}",
        ]
        
        try:
            create_time = datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')
            info.append(f"Created: {create_time}")
        except:
            pass
        
        try:
            info.append(f"User: {proc.username()}")
        except (psutil.AccessDenied, AttributeError):
            info.append("User: <Access Denied>")
        
        try:
            cmdline = proc.cmdline()
            if cmdline:
                info.append(f"Command: {' '.join(cmdline)}")
        except (psutil.AccessDenied, psutil.ZombieProcess):
            info.append("Command: <Access Denied>")
        
        return "\n".join(info)
    
    except psutil.NoSuchProcess:
        return f"Error: No process found with PID {pid}."
    except psutil.AccessDenied:
        return f"Error: Access denied to process {pid}. Try running with administrator privileges."
    except Exception as e:
        return f"Error getting process info: {str(e)}"


# @tool
# def kill_process(pid: int, force: bool = False) -> str:
#     """
#     Terminate a process by PID.
    
#     Args:
#         pid: Process ID to terminate
#         force: Use force kill instead of graceful termination (default: False)
    
#     Returns:
#         Success or error message
#     """
#     print(f"Killing process PID: {pid} (force={force})")
#     try:
#         proc = psutil.Process(pid)
#         proc_name = proc.name()
        
#         if force:
#             proc.kill()  # Windows: TerminateProcess, Unix: SIGKILL
#             return f"Process '{proc_name}' (PID: {pid}) force killed."
#         else:
#             proc.terminate()  # Windows: TerminateProcess with exit code, Unix: SIGTERM
#             return f"Process '{proc_name}' (PID: {pid}) terminated."
    
#     except psutil.NoSuchProcess:
#         return f"Error: No process found with PID {pid}."
#     except psutil.AccessDenied:
#         return f"Error: Access denied. Cannot kill process {pid}. Try running with administrator privileges."
#     except Exception as e:
#         return f"Error killing process: {str(e)}"


@tool
def get_system_info() -> str:
    """
    Get system resource usage information.
    
    Returns:
        System CPU, memory, and disk usage information
    """
    print("Getting system information")
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Get primary disk (C: on Windows, / on Unix)
        if platform.system() == 'Windows':
            disk = psutil.disk_usage('C:\\')
            disk_label = "Disk (C:)"
        else:
            disk = psutil.disk_usage('/')
            disk_label = "Disk (/)"
        
        info = [
            f"System Resource Usage (Platform: {platform.system()} {platform.release()}):",
            f"\nCPU:",
            f"  Usage: {cpu_percent}%",
            f"  Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical",
            f"\nMemory:",
            f"  Total: {memory.total / 1024 / 1024 / 1024:.1f} GB",
            f"  Used: {memory.used / 1024 / 1024 / 1024:.1f} GB ({memory.percent}%)",
            f"  Available: {memory.available / 1024 / 1024 / 1024:.1f} GB",
            f"\n{disk_label}:",
            f"  Total: {disk.total / 1024 / 1024 / 1024:.1f} GB",
            f"  Used: {disk.used / 1024 / 1024 / 1024:.1f} GB ({disk.percent}%)",
            f"  Free: {disk.free / 1024 / 1024 / 1024:.1f} GB",
        ]
        
        return "\n".join(info)
    
    except Exception as e:
        return f"Error getting system info: {str(e)}"


@tool
def find_process_by_name(name: str) -> str:
    """
    Find processes by name or partial name match.
    
    Args:
        name: Process name or partial name to search for (case-insensitive)
    
    Returns:
        List of matching processes with their PIDs
    """
    print(f"Finding processes matching: {name}")
    try:
        matches = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_name = proc.info['name']
                # Case-insensitive search
                if name.lower() in proc_name.lower():
                    matches.append(
                        f"PID: {proc.info['pid']} | {proc_name}\n"
                        f"  CPU: {proc.info['cpu_percent'] or 0:.1f}% | "
                        f"Memory: {proc.info['memory_percent'] or 0:.1f}%\n"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not matches:
            return f"No processes found matching '{name}'."
        
        return f"Found {len(matches)} process(es) matching '{name}':\n\n" + "\n".join(matches)
    
    except Exception as e:
        return f"Error finding processes: {str(e)}"


@tool
def list_disk_drives() -> str:
    """
    List all available disk drives (especially useful on Windows).
    
    Returns:
        List of disk drives with usage information
    """
    print("Listing disk drives")
    try:
        drives = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drives.append(
                    f"Drive: {partition.device}\n"
                    f"  Mount Point: {partition.mountpoint}\n"
                    f"  File System: {partition.fstype}\n"
                    f"  Total: {usage.total / 1024 / 1024 / 1024:.1f} GB\n"
                    f"  Used: {usage.used / 1024 / 1024 / 1024:.1f} GB ({usage.percent}%)\n"
                    f"  Free: {usage.free / 1024 / 1024 / 1024:.1f} GB\n"
                )
            except PermissionError:
                drives.append(
                    f"Drive: {partition.device}\n"
                    f"  Mount Point: {partition.mountpoint}\n"
                    f"  Status: <Access Denied>\n"
                )
        
        if not drives:
            return "No disk drives found."
        
        return "Available Disk Drives:\n\n" + "\n".join(drives)
    
    except Exception as e:
        return f"Error listing disk drives: {str(e)}"