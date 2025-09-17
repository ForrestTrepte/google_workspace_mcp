import asyncio
import webbrowser
import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_list_task_lists() -> None:
    # Connect to the HTTP server
    # NOTE: This requires:
    # 1. The HTTP server has been started, running separately from outside this test
    # 2. OAuth may pop up a web browser that needs to be completed manually during this test?
    #    Not sure what will happen when cached auth runs out.
    #    Will we need a test to call start_google_auth from a test? Or authenticate with MCP inspector before running this test?
    client = Client("http://localhost:8111/mcp", auth="oauth")
    async with client:
        result = await client.call_tool("list_task_lists", {})
        assert result is not None
