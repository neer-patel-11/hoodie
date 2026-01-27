import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional
import io

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Configuration
SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_PATH = Path("D:\AI_agents\hodie\drive_token.json")
CREDENTIALS_PATH = Path("D:\AI_agents\hodie\drive_credential.json")


class GoogleDriveMCPServer:
    def __init__(self):
        self.server = Server("google-drive-mcp")
        self.creds: Optional[Credentials] = None
        self.service = None
        self.setup_handlers()

    def load_credentials(self) -> None:
        """Load OAuth2 credentials and create Drive service."""
        creds = None
        
        # Load token if it exists
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        
        # If no valid credentials, raise error
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed credentials
                TOKEN_PATH.write_text(creds.to_json())
            else:
                raise Exception(
                    "No valid token found. Please run authentication first. "
                    "Get the auth URL by calling the 'get_auth_url' tool."
                )
        
        self.creds = creds
        self.service = build("drive", "v3", credentials=creds)

    def get_auth_url(self) -> str:
        """Generate OAuth2 authorization URL."""
        if not CREDENTIALS_PATH.exists():
            raise Exception(
                f"Credentials file not found at {CREDENTIALS_PATH}. "
                "Please download OAuth2 credentials from Google Cloud Console."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_PATH), SCOPES
        )
        # Use the out-of-band flow for CLI applications
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true"
        )
        
        return auth_url

    def save_token(self, code: str) -> None:
        """Save OAuth2 token from authorization code."""
        if not CREDENTIALS_PATH.exists():
            raise Exception(f"Credentials file not found at {CREDENTIALS_PATH}")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_PATH), SCOPES
        )
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save credentials
        TOKEN_PATH.write_text(creds.to_json())
        
        self.creds = creds
        self.service = build("drive", "v3", credentials=creds)

    
    def setup_handlers(self):
        """Set up MCP request handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="get_auth_url",
                    description="Get OAuth2 authorization URL for Google Drive access",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="save_auth_token",
                    description="Save OAuth2 authorization code after user grants access",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Authorization code from OAuth2 callback",
                            },
                        },
                        "required": ["code"],
                    },
                ),
                Tool(
                    name="list_files",
                    description="List files in Google Drive with optional search query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., \"name contains 'report'\")",
                            },
                            "page_size": {
                                "type": "number",
                                "description": "Number of files to return (default: 100)",
                            },
                        },
                    },
                ),
                Tool(
                    name="read_file",
                    description="Read content of a file by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {
                                "type": "string",
                                "description": "Google Drive file ID",
                            },
                        },
                        "required": ["file_id"],
                    },
                ),
                Tool(
                    name="write_file",
                    description="Create a new file in Google Drive",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "File name",
                            },
                            "content": {
                                "type": "string",
                                "description": "File content",
                            },
                            "mime_type": {
                                "type": "string",
                                "description": "MIME type (default: text/plain)",
                            },
                            "folder_id": {
                                "type": "string",
                                "description": "Parent folder ID (optional)",
                            },
                        },
                        "required": ["name", "content"],
                    },
                ),
                Tool(
                    name="update_file",
                    description="Update an existing file's content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {
                                "type": "string",
                                "description": "Google Drive file ID",
                            },
                            "content": {
                                "type": "string",
                                "description": "New file content",
                            },
                        },
                        "required": ["file_id", "content"],
                    },
                ),
                Tool(
                    name="delete_file",
                    description="Delete a file by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {
                                "type": "string",
                                "description": "Google Drive file ID",
                            },
                        },
                        "required": ["file_id"],
                    },
                ),
                Tool(
                    name="create_folder",
                    description="Create a new folder in Google Drive",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Folder name",
                            },
                            "parent_id": {
                                "type": "string",
                                "description": "Parent folder ID (optional)",
                            },
                        },
                        "required": ["name"],
                    },
                ),
                Tool(
                    name="test_credentials",
                    description="Test whether Google Drive credentials are valid",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),

                Tool(
                    name="search_files",
                    description="Search for files using Google Drive query syntax",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Google Drive search query",
                            },
                        },
                        "required": ["query"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            try:
                if name == "get_auth_url":
                    url = self.get_auth_url()
                    return [
                        TextContent(
                            type="text",
                            text=f"Please visit this URL to authorize access:\n\n{url}\n\n"
                            f"After authorizing, copy the code and use the 'save_auth_token' tool.",
                        )
                    ]

                elif name == "save_auth_token":
                    self.save_token(arguments["code"])
                    return [
                        TextContent(
                            type="text",
                            text="Authorization successful! You can now use Google Drive tools.",
                        )
                    ]
                elif name == "test_credentials":
                    info = self.test_credentials()
                    return [
                        TextContent(
                            type="text",
                            text=(
                                "✅ Credentials are valid!\n\n"
                                f"Email: {info['email']}\n"
                                f"Name: {info['display_name']}\n"
                                f"Storage Used: {info['usage']} / {info['limit']}"
                            ),
                        )
                    ]

                elif name == "list_files":
                    if not self.service:
                        self.load_credentials()
                    
                    results = self.service.files().list(
                        pageSize=arguments.get("page_size", 100),
                        fields="files(id, name, mimeType, size, modifiedTime, createdTime)",
                        q=arguments.get("query"),
                    ).execute()
                    
                    files = results.get("files", [])
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(files, indent=2),
                        )
                    ]

                elif name == "read_file":
                    if not self.service:
                        self.load_credentials()
                    
                    request = self.service.files().get_media(fileId=arguments["file_id"])
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    
                    done = False
                    while not done:
                        _, done = downloader.next_chunk()
                    
                    content = fh.getvalue().decode("utf-8")
                    return [TextContent(type="text", text=content)]

                elif name == "write_file":
                    if not self.service:
                        self.load_credentials()
                    
                    file_metadata = {"name": arguments["name"]}
                    
                    if "folder_id" in arguments:
                        file_metadata["parents"] = [arguments["folder_id"]]
                    
                    media = MediaIoBaseUpload(
                        io.BytesIO(arguments["content"].encode("utf-8")),
                        mimetype=arguments.get("mime_type", "text/plain"),
                    )
                    
                    file = self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields="id, name, mimeType",
                    ).execute()
                    
                    return [
                        TextContent(
                            type="text",
                            text=f"File created successfully:\n{json.dumps(file, indent=2)}",
                        )
                    ]

                elif name == "update_file":
                    if not self.service:
                        self.load_credentials()
                    
                    media = MediaIoBaseUpload(
                        io.BytesIO(arguments["content"].encode("utf-8")),
                        mimetype="text/plain",
                    )
                    
                    file = self.service.files().update(
                        fileId=arguments["file_id"],
                        media_body=media,
                        fields="id, name, mimeType, modifiedTime",
                    ).execute()
                    
                    return [
                        TextContent(
                            type="text",
                            text=f"File updated successfully:\n{json.dumps(file, indent=2)}",
                        )
                    ]

                elif name == "delete_file":
                    if not self.service:
                        self.load_credentials()
                    
                    self.service.files().delete(fileId=arguments["file_id"]).execute()
                    
                    return [
                        TextContent(
                            type="text",
                            text=f"File {arguments['file_id']} deleted successfully.",
                        )
                    ]

                elif name == "create_folder":
                    if not self.service:
                        self.load_credentials()
                    
                    file_metadata = {
                        "name": arguments["name"],
                        "mimeType": "application/vnd.google-apps.folder",
                    }
                    
                    if "parent_id" in arguments:
                        file_metadata["parents"] = [arguments["parent_id"]]
                    
                    folder = self.service.files().create(
                        body=file_metadata,
                        fields="id, name",
                    ).execute()
                    
                    return [
                        TextContent(
                            type="text",
                            text=f"Folder created successfully:\n{json.dumps(folder, indent=2)}",
                        )
                    ]

                elif name == "search_files":
                    if not self.service:
                        self.load_credentials()
                    
                    results = self.service.files().list(
                        q=arguments["query"],
                        fields="files(id, name, mimeType, size, modifiedTime)",
                    ).execute()
                    
                    files = results.get("files", [])
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(files, indent=2),
                        )
                    ]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

    def test_credentials(self) -> dict:
        """Test whether the stored credentials are valid."""
        if not self.service:
            self.load_credentials()

        # This endpoint is very cheap and auth-protected
        about = self.service.about().get(fields="user, storageQuota").execute()

        return {
            "email": about["user"]["emailAddress"],
            "display_name": about["user"]["displayName"],
            "limit": about["storageQuota"]["limit"],
            "usage": about["storageQuota"]["usage"],
        }
    
# For generating drive_token.json
# async def main():
#     server = GoogleDriveMCPServer()

#     # 1. Get auth URL
#     url = server.get_auth_url()
#     print("Open this URL in your browser:\n", url)

#     # 2. Manually paste the code
#     code = input("\nPaste the authorization code here: ").strip()

#     # 3. Exchange code for token
#     server.save_token(code)

#     # 4. Verify credentials
#     info = server.test_credentials()
#     print("✅ Auth OK for:", info["email"])

async def main():
    server = GoogleDriveMCPServer()
    
    #  start MCP server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())