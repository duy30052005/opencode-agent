"""Debug MCP Docker connection directly."""
import asyncio
import sys
sys.path.insert(0, '.')

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.config import settings

TOKEN = settings.GITHUB_TOKEN.strip()
print(f"Using token: {TOKEN[:20]}...")

async def test_mcp():
    params = StdioServerParameters(
        command="docker",
        args=["run", "-i", "--rm",
              "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
              "ghcr.io/github/github-mcp-server",
              "stdio"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": TOKEN},
    )
    print("Connecting to Docker MCP server...")
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Initializing session...")
                result = await session.initialize()
                print(f"✅ Connected! Server: {result.serverInfo.name} v{result.serverInfo.version}")

                # List available tools
                tools = await session.list_tools()
                print(f"✅ Available tools: {len(tools.tools)}")
                for t in tools.tools[:5]:
                    print(f"   - {t.name}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_mcp())
