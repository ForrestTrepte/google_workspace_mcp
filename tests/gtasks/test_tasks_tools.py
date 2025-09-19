import asyncio
import re
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
    # 2. OAuth may pop up a web browser that needs to be completed manually during this test
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


@pytest.mark.asyncio
async def test_list_tasks_subtasks() -> None:
    client = Client("http://localhost:8111/mcp", auth="oauth")
    async with client:
        result = await client.call_tool(
            "list_tasks",
            {
                "task_list_id": connector_test_task_list_ID,
            },
        )
        result_lines = result.data.split("\n")
        bullet_lines = [
            line.rstrip()
            for line in result_lines
            if line.strip().startswith("- ") or line.strip().startswith("* ")
        ]
        task_infos = [get_task_info(bullet_line) for bullet_line in bullet_lines]
        task_names = [task_info.name for task_info in task_infos]

        first_task_index = task_names.index("First task")
        assert first_task_index >= 0
        check_task_info(task_infos, "First task", first_task_index, "-", 0)
        check_task_info(task_infos, "Second task", first_task_index + 1, "-", 0)
        check_task_info(task_infos, "Second task, subtask 1", first_task_index + 2, "-", 0)
        check_task_info(task_infos, "Second task, subtask 2", first_task_index + 3, "-", 0)
        check_task_info(task_infos, "Third task", first_task_index + 4, "-", 0)


class TaskInfo:
    def __init__(self, name: str, id: str, bullet_char: str, indent: int) -> None:
        self.name = name
        self.id = id
        self.bullet_char = bullet_char
        self.indent = indent


def get_task_info(bullet_line: str) -> TaskInfo:
    # Pattern to match: (optional whitespace)(bullet char)(space)(task name)(space)(ID: )(id)(closing paren)
    pattern = (
        r"^(?P<indent>\s*)(?P<bullet>[*-])\s+(?P<name>.+?)\s+\(ID:\s+(?P<id>[^)]+)\)"
    )
    match = re.match(pattern, bullet_line)

    if not match:
        raise ValueError(f"Invalid bullet line format: {bullet_line}")

    return TaskInfo(
        name=match.group("name"),
        id=match.group("id"),
        bullet_char=match.group("bullet"),
        indent=len(match.group("indent")),
    )


def check_task_info(
    task_infos: list[TaskInfo],
    expected_name: str,
    expected_index: int,
    expected_bullet_char: str,
    expected_indent: int,
) -> None:
    index = -1
    for index in range(len(task_infos)):
        if task_infos[index].name == expected_name:
            break
        index += 1
    assert index == expected_index

    task_info = task_infos[index]
    assert task_info.bullet_char == expected_bullet_char
    assert task_info.indent == expected_indent
