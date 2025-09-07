import asyncio
import webbrowser
import pytest
from fastmcp import Client

import gtasks.tasks_tools  # registers @server.tool() functions
from core.server import server  # SecureFastMCP(...)


@pytest.mark.asyncio
async def test_list_task_lists() -> None:
    client = Client(server)
    async with client:
        result = await client.call_tool(
            "start_google_auth",
            {
                "service_name": "",
                "user_google_email": "your_email@gmail.com", # TODO: replace with a real email
            },
        )
        assert result is not None
        authorization_text = "Authorization URL:"
        assert authorization_text in result.data
        authorization_start = result.data.index(authorization_text) + len(authorization_text)
        authorization_end = result.data.index("\n", authorization_start)
        authorization_url = result.data[authorization_start:authorization_end].strip()
        assert authorization_url.startswith("https://accounts.google.com/o/oauth2/auth?")
        # TODO: Remove hack to open the URL in a browser and complete the OAuth flow manually?
        webbrowser.open_new_tab(authorization_url)
        await asyncio.sleep(30)
        # This next part
        # TODO: This doesn't actually work because the full server isn't running to receive the oauth callback?
        result = await client.call_tool("list_task_lists", {})
        assert result is not None
