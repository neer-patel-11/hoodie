"""
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["/path/to/github_mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
"""

import os
import json
import asyncio
from typing import Any
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server


# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable must be set")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


async def github_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make a request to the GitHub API"""
    url = f"{GITHUB_API_BASE}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=HEADERS)
        elif method == "POST":
            response = await client.post(url, headers=HEADERS, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=HEADERS, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=HEADERS)
        
        response.raise_for_status()
        return response.json() if response.content else {}


# Initialize MCP server
app = Server("github-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitHub tools"""
    return [
        Tool(
            name="get_username",
            description="Get the authenticated user's GitHub username and profile information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_repos_list",
            description="Get list of repositories for the authenticated user or a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username (optional, defaults to authenticated user)"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["all", "owner", "member"],
                        "description": "Type of repositories to list (default: owner)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["created", "updated", "pushed", "full_name"],
                        "description": "Sort order (default: updated)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_specific_repo",
            description="Get detailed information about a specific repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="get_commits",
            description="Get commit history for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "sha": {
                        "type": "string",
                        "description": "Branch name or commit SHA (optional)"
                    },
                    "per_page": {
                        "type": "number",
                        "description": "Number of commits to return (max 100, default 30)"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="get_specific_commit",
            description="Get details of a specific commit",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "sha": {
                        "type": "string",
                        "description": "Commit SHA"
                    }
                },
                "required": ["owner", "repo", "sha"]
            }
        ),
        Tool(
            name="get_pull_requests",
            description="Get list of pull requests for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "description": "PR state (default: open)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["created", "updated", "popularity", "long-running"],
                        "description": "Sort order (default: created)"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="get_specific_pr",
            description="Get details of a specific pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "pr_number": {
                        "type": "number",
                        "description": "Pull request number"
                    }
                },
                "required": ["owner", "repo", "pr_number"]
            }
        ),
        Tool(
            name="get_issues",
            description="Get list of issues for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "description": "Issue state (default: open)"
                    },
                    "labels": {
                        "type": "string",
                        "description": "Comma-separated list of label names"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="get_branches",
            description="Get list of branches for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="get_file_contents",
            description="Get contents of a file from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "path": {
                        "type": "string",
                        "description": "File path in the repository"
                    },
                    "ref": {
                        "type": "string",
                        "description": "Branch name, tag, or commit SHA (optional)"
                    }
                },
                "required": ["owner", "repo", "path"]
            }
        ),
        Tool(
            name="create_issue",
            description="Create a new issue in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner username"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue body/description"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of label names"
                    }
                },
                "required": ["owner", "repo", "title"]
            }
        ),
         Tool(
            name="search_repositories",
            description="Search for repositories on GitHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'language:python stars:>1000')"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["stars", "forks", "updated"],
                        "description": "Sort field (default: best match)"
                    },
                    "per_page": {
                        "type": "number",
                        "description": "Results per page (max 100, default 30)"
                    }
                },
                "required": ["query"]
            }
        )
     ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "get_username":
            data = await github_api_request("/user")
            result = {
                "login": data.get("login"),
                "name": data.get("name"),
                "email": data.get("email"),
                "bio": data.get("bio"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "following": data.get("following"),
                "created_at": data.get("created_at"),
                "avatar_url": data.get("avatar_url")
            }
            
        elif name == "get_repos_list":
            username = arguments.get("username")
            repo_type = arguments.get("type", "owner")
            sort = arguments.get("sort", "updated")
            
            if username:
                endpoint = f"/users/{username}/repos?sort={sort}"
            else:
                endpoint = f"/user/repos?type={repo_type}&sort={sort}"
            
            data = await github_api_request(endpoint)
            result = [{
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description"),
                "private": repo["private"],
                "html_url": repo["html_url"],
                "language": repo.get("language"),
                "stargazers_count": repo["stargazers_count"],
                "forks_count": repo["forks_count"],
                "updated_at": repo["updated_at"]
            } for repo in data]
            
        elif name == "get_specific_repo":
            owner = arguments["owner"]
            repo = arguments["repo"]
            data = await github_api_request(f"/repos/{owner}/{repo}")
            result = {
                "name": data["name"],
                "full_name": data["full_name"],
                "description": data.get("description"),
                "private": data["private"],
                "html_url": data["html_url"],
                "language": data.get("language"),
                "stargazers_count": data["stargazers_count"],
                "forks_count": data["forks_count"],
                "open_issues_count": data["open_issues_count"],
                "default_branch": data["default_branch"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "size": data["size"],
                "topics": data.get("topics", [])
            }
            
        elif name == "get_commits":
            owner = arguments["owner"]
            repo = arguments["repo"]
            sha = arguments.get("sha", "")
            per_page = arguments.get("per_page", 30)
            
            endpoint = f"/repos/{owner}/{repo}/commits?per_page={per_page}"
            if sha:
                endpoint += f"&sha={sha}"
            
            data = await github_api_request(endpoint)
            result = [{
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "url": commit["html_url"]
            } for commit in data]
            
        elif name == "get_specific_commit":
            owner = arguments["owner"]
            repo = arguments["repo"]
            sha = arguments["sha"]
            
            data = await github_api_request(f"/repos/{owner}/{repo}/commits/{sha}")
            result = {
                "sha": data["sha"],
                "message": data["commit"]["message"],
                "author": data["commit"]["author"]["name"],
                "date": data["commit"]["author"]["date"],
                "url": data["html_url"],
                "stats": data.get("stats"),
                "files": [{
                    "filename": f["filename"],
                    "status": f["status"],
                    "additions": f["additions"],
                    "deletions": f["deletions"],
                    "changes": f["changes"]
                } for f in data.get("files", [])]
            }
            
        elif name == "get_pull_requests":
            owner = arguments["owner"]
            repo = arguments["repo"]
            state = arguments.get("state", "open")
            sort = arguments.get("sort", "created")
            
            data = await github_api_request(
                f"/repos/{owner}/{repo}/pulls?state={state}&sort={sort}"
            )
            result = [{
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "user": pr["user"]["login"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "html_url": pr["html_url"],
                "head": pr["head"]["ref"],
                "base": pr["base"]["ref"]
            } for pr in data]
            
        elif name == "get_specific_pr":
            owner = arguments["owner"]
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            
            data = await github_api_request(f"/repos/{owner}/{repo}/pulls/{pr_number}")
            result = {
                "number": data["number"],
                "title": data["title"],
                "body": data.get("body"),
                "state": data["state"],
                "user": data["user"]["login"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "merged": data.get("merged", False),
                "mergeable": data.get("mergeable"),
                "html_url": data["html_url"],
                "head": data["head"]["ref"],
                "base": data["base"]["ref"],
                "commits": data["commits"],
                "additions": data["additions"],
                "deletions": data["deletions"],
                "changed_files": data["changed_files"]
            }
            
        elif name == "get_issues":
            owner = arguments["owner"]
            repo = arguments["repo"]
            state = arguments.get("state", "open")
            labels = arguments.get("labels", "")
            
            endpoint = f"/repos/{owner}/{repo}/issues?state={state}"
            if labels:
                endpoint += f"&labels={labels}"
            
            data = await github_api_request(endpoint)
            result = [{
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "user": issue["user"]["login"],
                "labels": [label["name"] for label in issue.get("labels", [])],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "html_url": issue["html_url"]
            } for issue in data if "pull_request" not in issue]
            
        elif name == "get_branches":
            owner = arguments["owner"]
            repo = arguments["repo"]
            
            data = await github_api_request(f"/repos/{owner}/{repo}/branches")
            result = [{
                "name": branch["name"],
                "protected": branch.get("protected", False),
                "commit_sha": branch["commit"]["sha"]
            } for branch in data]
            
        elif name == "get_file_contents":
            owner = arguments["owner"]
            repo = arguments["repo"]
            path = arguments["path"]
            ref = arguments.get("ref", "")
            
            endpoint = f"/repos/{owner}/{repo}/contents/{path}"
            if ref:
                endpoint += f"?ref={ref}"
            
            data = await github_api_request(endpoint)
            
            # Decode base64 content if it's a file
            import base64
            if data.get("content"):
                content = base64.b64decode(data["content"]).decode("utf-8")
            else:
                content = None
            
            result = {
                "name": data["name"],
                "path": data["path"],
                "sha": data["sha"],
                "size": data["size"],
                "type": data["type"],
                "content": content,
                "html_url": data["html_url"]
            }
            
        elif name == "create_issue":
            owner = arguments["owner"]
            repo = arguments["repo"]
            title = arguments["title"]
            body = arguments.get("body", "")
            labels = arguments.get("labels", [])
            
            payload = {
                "title": title,
                "body": body,
                "labels": labels
            }
            
            data = await github_api_request(
                f"/repos/{owner}/{repo}/issues",
                method="POST",
                data=payload
            )
            result = {
                "number": data["number"],
                "title": data["title"],
                "state": data["state"],
                "html_url": data["html_url"],
                "created_at": data["created_at"]
            }
            
        elif name == "search_repositories":
            query = arguments["query"]
            sort = arguments.get("sort", "")
            per_page = arguments.get("per_page", 30)
            
            endpoint = f"/search/repositories?q={query}&per_page={per_page}"
            if sort:
                endpoint += f"&sort={sort}"
            
            data = await github_api_request(endpoint)
            result = {
                "total_count": data["total_count"],
                "items": [{
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "html_url": repo["html_url"],
                    "language": repo.get("language"),
                    "stargazers_count": repo["stargazers_count"],
                    "forks_count": repo["forks_count"]
                } for repo in data["items"]]
            }
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except httpx.HTTPStatusError as e:
        return [TextContent(
            type="text",
            text=f"GitHub API error: {e.response.status_code} - {e.response.text}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())