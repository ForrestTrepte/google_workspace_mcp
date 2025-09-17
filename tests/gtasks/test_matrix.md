# Test Matrix

## Tests for verifying Google Tasks functionality

| | automated ([test_tasks_tools](./test_tasks_tools.py)) | MCP inspector| Claude desktop |
| --- | --- | --- | --- |
| list_task_lists | ✅ | ✅ | ✅ |
| list_task_lists with max_results | ❌ | ✅ | ✅ |
| list_tasks | ✅ | ❌ | ✅ |
| list_tasks with max_results | ✅ | ❌ | ✅ |
| list_tasks with completed | ✅ | ❌ | ✅ |

## Claude desktop prompts

```
Execute the following test cases to verify if the google_workspace MCP connector is working correctly:
* Call list_task_lists
* Call list_task_lists with max_results=2
* Call list_tasks with task_list_id=d0R6V2pRalU5M0d2MkNFZQ
* Call list_tasks with task_list_id=d0R6V2pRalU5M0d2MkNFZQ, max_results=2
* Call list_tasks with task_list_id=d0R6V2pRalU5M0d2MkNFZQ, show_completed=false, show_hidden=false
* Call list_tasks with task_list_id=d0R6V2pRalU5M0d2MkNFZQ, show_completed=true, show_hidden=true

No need to use the outputs to do anything or put them into your output, just make the calls and state whether they successfully produced a valid response.
```
