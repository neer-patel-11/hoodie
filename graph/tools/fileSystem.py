from langchain_core.tools import tool
import os
import shutil
import platform
from pathlib import Path
from typing import  Optional
from datetime import datetime

# ============================================
# FILE SYSTEM TOOLS (Cross-platform)
# ============================================

@tool
def list_directory(path: str = ".") -> str:
    """
    List contents of a directory with details.
    
    Args:
        path: Directory path to list (default: current directory)
    
    Returns:
        Formatted string with file/folder names, sizes, and types
    """
    print(f"Listing directory: {path}")
    try:
        # Handle Windows paths properly
        path_obj = Path(path).resolve()
        
        if not path_obj.exists():
            return f"Error: Path '{path}' does not exist."
        
        if not path_obj.is_dir():
            return f"Error: '{path}' is not a directory."
        
        items = []
        for item in sorted(path_obj.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            
            try:
                size = item.stat().st_size if item.is_file() else "-"
                size_str = f"{size:,} bytes" if size != "-" else "-"
            except (PermissionError, OSError):
                size_str = "<Access Denied>"
            
            items.append(
                f"[{item_type}] {item.name}\n"
                f"  Size: {size_str}\n"
                f"  Path: {item}\n"
            )
        
        if not items:
            return f"Directory '{path}' is empty."
        
        return f"Contents of '{path}':\n\n" + "\n".join(items)
    
    except PermissionError:
        return f"Error: Permission denied to access '{path}'."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def read_file(file_path: str, max_lines: Optional[int] = None) -> str:
    """
    Read and return contents of a text file.
    
    Args:
        file_path: Path to the file to read
        max_lines: Maximum number of lines to read (default: all lines)
    
    Returns:
        File contents as string
    """
    print(f"Reading file: {file_path}")
    try:
        path_obj = Path(file_path).resolve()
        
        if not path_obj.exists():
            return f"Error: File '{file_path}' does not exist."
        
        if not path_obj.is_file():
            return f"Error: '{file_path}' is not a file."
        
        # Try different encodings for Windows compatibility
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(path_obj, 'r', encoding=encoding) as f:
                    if max_lines:
                        lines = [f.readline() for _ in range(max_lines)]
                        content = "".join(lines)
                    else:
                        content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            return f"Error: Unable to decode '{file_path}'. It may be a binary file."
        
        if max_lines:
            return f"First {max_lines} lines of '{file_path}' (encoding: {used_encoding}):\n\n{content}"
        else:
            return f"Contents of '{file_path}' (encoding: {used_encoding}):\n\n{content}"
    
    except PermissionError:
        return f"Error: Permission denied to read '{file_path}'."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str, mode: str = "w") -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        mode: Write mode - 'w' for overwrite, 'a' for append (default: 'w')
    
    Returns:
        Success or error message
    """
    print(f"Writing to file: {file_path}")
    try:
        if mode not in ['w', 'a']:
            return "Error: mode must be 'w' (write) or 'a' (append)."
        
        path_obj = Path(file_path).resolve()
        
        # Create parent directories if they don't exist
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Use UTF-8 with BOM for Windows compatibility if needed
        with open(path_obj, mode, encoding='utf-8', newline='') as f:
            f.write(content)
        
        action = "Written" if mode == 'w' else "Appended"
        return f"{action} {len(content)} characters to '{file_path}' successfully."
    
    except PermissionError:
        return f"Error: Permission denied to write to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def delete_file_or_folder(path: str) -> str:
    """
    Delete a file or folder.
    
    Args:
        path: Path to the file or folder to delete
    
    Returns:
        Success or error message
    """
    print(f"Deleting: {path}")
    try:
        path_obj = Path(path).resolve()
        
        if not path_obj.exists():
            return f"Error: Path '{path}' does not exist."
        
        if path_obj.is_file():
            # Windows may need special handling for read-only files
            if platform.system() == 'Windows':
                os.chmod(path_obj, 0o777)
            path_obj.unlink()
            return f"File '{path}' deleted successfully."
        elif path_obj.is_dir():
            # Windows-compatible recursive delete
            shutil.rmtree(path_obj, ignore_errors=False)
            return f"Folder '{path}' and all its contents deleted successfully."
    
    except PermissionError:
        return f"Error: Permission denied to delete '{path}'. File may be in use or read-only."
    except Exception as e:
        return f"Error deleting: {str(e)}"


@tool
def create_folder(path: str) -> str:
    """
    Create a new folder (creates parent directories if needed).
    
    Args:
        path: Path of the folder to create
    
    Returns:
        Success or error message
    """
    print(f"Creating folder: {path}")
    try:
        path_obj = Path(path).resolve()
        path_obj.mkdir(parents=True, exist_ok=True)
        return f"Folder '{path}' created successfully."
    
    except PermissionError:
        return f"Error: Permission denied to create folder '{path}'."
    except Exception as e:
        return f"Error creating folder: {str(e)}"


@tool
def search_files(directory: str, pattern: str, recursive: bool = True) -> str:
    """
    Search for files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., '*.py', 'test_*')
        recursive: Search subdirectories recursively (default: True)
    
    Returns:
        List of matching file paths
    """
    print(f"Searching for '{pattern}' in {directory}")
    try:
        path_obj = Path(directory).resolve()
        
        if not path_obj.exists():
            return f"Error: Directory '{directory}' does not exist."
        
        if not path_obj.is_dir():
            return f"Error: '{directory}' is not a directory."
        
        matches = []
        if recursive:
            try:
                matches = list(path_obj.rglob(pattern))
            except PermissionError:
                # Fallback if permission denied on some subdirectories
                matches = [m for m in path_obj.rglob(pattern)]
        else:
            matches = list(path_obj.glob(pattern))
        
        if not matches:
            return f"No files matching '{pattern}' found in '{directory}'."
        
        results = [f"- {match}" for match in matches]
        return f"Found {len(matches)} file(s) matching '{pattern}':\n\n" + "\n".join(results)
    
    except PermissionError:
        return f"Error: Permission denied to search in '{directory}'."
    except Exception as e:
        return f"Error searching files: {str(e)}"


@tool
def get_file_info(path: str) -> str:
    """
    Get detailed information about a file or folder.
    
    Args:
        path: Path to the file or folder
    
    Returns:
        Detailed information about the file/folder
    """
    print(f"Getting info for: {path}")
    try:
        path_obj = Path(path).resolve()
        
        if not path_obj.exists():
            return f"Error: Path '{path}' does not exist."
        
        stat = path_obj.stat()
        
        info = [
            f"Path: {path_obj}",
            f"Type: {'Directory' if path_obj.is_dir() else 'File'}",
            f"Size: {stat.st_size:,} bytes" if path_obj.is_file() else "Size: -",
            f"Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Accessed: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        # Windows-specific attributes
        if platform.system() == 'Windows':
            import stat as stat_module
            attrs = []
            if stat.st_file_attributes & stat_module.FILE_ATTRIBUTE_HIDDEN:
                attrs.append("Hidden")
            if stat.st_file_attributes & stat_module.FILE_ATTRIBUTE_READONLY:
                attrs.append("Read-only")
            if stat.st_file_attributes & stat_module.FILE_ATTRIBUTE_SYSTEM:
                attrs.append("System")
            if attrs:
                info.append(f"Attributes: {', '.join(attrs)}")
        
        return "\n".join(info)
    
    except Exception as e:
        return f"Error getting file info: {str(e)}"

