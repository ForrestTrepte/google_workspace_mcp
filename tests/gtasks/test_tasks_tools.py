import asyncio
import webbrowser
import pytest
from fastmcp import Client

# TODO: This assumes that a specific Google account is used for testing that has this particular task list.
#   Ideally, there would be test setup that creates the task lists needed for testing.
connector_test_task_list_ID = "d0R6V2pRalU5M0d2MkNFZQ"


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
        assert f"Connector test (ID: {connector_test_task_list_ID})" in result.data
        assert result.data.count("(ID: ") > 2


@pytest.mark.asyncio
async def test_list_task_lists_max_results() -> None:
    client = Client("http://localhost:8111/mcp", auth="oauth")
    async with client:
        result = await client.call_tool("list_task_lists", {"max_results": 2})
        assert result is not None
        # each task list in result has the string "(ID: <some id>)"
        assert result.data.count("(ID: ") == 2


@pytest.mark.asyncio
async def test_list_tasks() -> None:
    client = Client("http://localhost:8111/mcp", auth="oauth")
    async with client:
        result = await client.call_tool(
            "list_tasks",
            {
                "task_list_id": connector_test_task_list_ID,
            },
        )
        assert result.data.count("(ID: ") > 2


@pytest.mark.asyncio
async def test_list_tasks_max_results() -> None:
    client = Client("http://localhost:8111/mcp", auth="oauth")
    async with client:
        result = await client.call_tool(
            "list_tasks",
            {
                "task_list_id": connector_test_task_list_ID,
                "max_results": 2,
            },
        )
        assert result.data.count("(ID: ") == 2


@pytest.mark.asyncio
async def test_list_tasks_show_completed() -> None:
    client = Client("http://localhost:8111/mcp", auth="oauth")
    async with client:
        # Get without completed
        result = await client.call_tool(
            "list_tasks",
            {
                "task_list_id": connector_test_task_list_ID,
                "show_completed": False,
                "show_hidden": False,
            },
        )
        assert "Status: completed" not in result.data
        no_completed_count = result.data.count("(ID: ")
        assert no_completed_count > 2

        # Get with completed (and hidden, because the completed tasks are also hidden)
        result = await client.call_tool(
            "list_tasks",
            {
                "task_list_id": connector_test_task_list_ID,
                "show_completed": True,
                "show_hidden": True,
            },
        )
        assert "Status: completed" in result.data
        completed_count = result.data.count("(ID: ")
        assert completed_count > no_completed_count
