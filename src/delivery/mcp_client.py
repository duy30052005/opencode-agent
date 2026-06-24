import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.config import settings

def _server_params(token: str) -> StdioServerParameters:
      return StdioServerParameters(
          command="docker",
          args=["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server"],
          env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},   # <-- per user, per session
      )

# call tool return error if failed
async def _call(session: ClientSession, name: str, args: dict):
  """Call a tool, raise on error, return the text payload"""
  result = await session.call_tool(name, args)
  if result.isError:
    text = result.content[0].text if result.content else 'unknown error'
    raise RuntimeError(f"MCP tool '{name}' failed: {text}")
  return result.content[0].text if result.content else ""

async def _ensure_branch(session: ClientSession, owner: str, repo: str,
                         branch: str, base: str) -> None:
  """Create the feature branch off `base`; reuse it if it already exists."""
  try:
    await _call(session, 'create_branch', {
      "owner": owner, "repo": repo,
      "branch": branch, "from_branch": base,
    })
  except RuntimeError as e:
    if "already exists" in str(e).lower():
      return            # branch is already there → reuse it
    raise

async def _deliver_async(token: str, branch: str, path: str, content: str,
                         title: str, body: str, base: str = 'main') -> str:
  owner, repo = settings.GITHUB_OWNER, settings.GITHUB_REPO
  async with stdio_client(_server_params(token)) as (read,write):
    async with ClientSession(read,write) as session:
      await session.initialize()
      # create (or reuse) the feature branch off base:
      await _ensure_branch(session, owner, repo, branch, base)
      # commit the file (push_files upserts: creates OR updates, no sha needed)
      await _call(session, "push_files", {
        "owner": owner, "repo": repo,
        "branch": branch,
        "files": [{"path": path, "content": content}],
        "message": f"Add/update {path} via OpenCode Agent",
      })
      #open PR: head = feature branch, base = main
      return await _call(session, "create_pull_request", {
        "owner": owner, "repo": repo,
        "title": title, "head": branch, "base": base, "body": body
      })

def deliver_via_mcp(token: str, branch: str, path, content: str,
                    title: str, body: str, base: str = "main") -> str:
  """Sync wrapper so the CLI/orchestrator can call it normally"""
  return asyncio.run(_deliver_async(token, branch, path, content, title, body, base))

