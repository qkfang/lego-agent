import inspect
import json
from typing import Any, Union
from prompty.tracer import trace

from azure.ai.projects.models import (
    AsyncAgentEventHandler,
    RunStep,
    ThreadMessage,
    ThreadRun,
    SubmitToolOutputsAction,
    RequiredFunctionToolCall,
    ToolOutput,
)

from azure.ai.projects.aio import AIProjectClient

from model import AgentUpdateEvent, Content, Function


class SustineoAgentEventHandler(AsyncAgentEventHandler[str]):

    def __init__(
        self,
        project_client: AIProjectClient,
        tools: dict[str, Function],
        notify: AgentUpdateEvent,
    ) -> None:
        super().__init__()
        self.notify = notify
        self.tools = tools
        self.project_client = project_client
        self.history: list[dict[str, Any]] = []

    @trace(name="send_agent_status")
    async def add_message(
        self,
        message: Union[ThreadMessage, ThreadRun, RunStep],
    ) -> None:
        last_message = self.history[-1] if self.history else None
        # if the last message is the same as the current one, skip it
        # this is to avoid duplicate messages in the history
        if (
            last_message
            and last_message["id"] == message["id"]
            and last_message["status"] == message["status"]
            and last_message["object"] == message["object"]
        ):
            return

        status = message["status"].replace("_", " ")

        if isinstance(message, ThreadRun):
            await self.notify(
                id=message.id,
                status=f"run {status}",
            )

        elif isinstance(message, RunStep):

            type = message["type"].replace("_", " ")
            if message.status == "completed" and message.type == "tool_calls":
                tool_calls: list[dict[str, Any]] = message.step_details.as_dict()[
                    "tool_calls"
                ]

                items = [
                    {
                        "id": tool_call["id"],
                        "type": tool_call["type"],
                        **{
                            key: value
                            for key, value in tool_call[tool_call["type"]].items()
                        },
                    }
                    for tool_call in tool_calls
                ]

                await self.notify(
                    id=message.id,
                    status=f'step "{type}" {status}',
                    content=Content(type="tool_calls", content=items),
                )
            else:
                await self.notify(
                    id=message.id,
                    status=f'step "{type}" {status}',
                )
        elif isinstance(message, ThreadMessage):
            if message.status == "completed":
                text: list[dict[str, Any]] = [m.as_dict() for m in message.content]
                items = [
                    {
                        "type": m["type"],
                        **m[m["type"]],
                    }
                    for m in text
                ]

                await self.notify(
                    id=message.id,
                    status=f"message {status}",
                    information="Acquired Result",
                    content=Content(type="text", content=items),
                    output=True,
                )

            else:
                await self.notify(
                    id=message.id,
                    status=f"message {status}",
                )

        self.history.append(message.as_dict())

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        await self.add_message(message)

    async def on_thread_run(self, run: "ThreadRun") -> None:
        # send message
        await self.add_message(run)

        # execute required tools
        if run.status == "requires_action" and isinstance(
            run.required_action, SubmitToolOutputsAction
        ):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredFunctionToolCall):
                    try:
                        output = await self.execute_tool_call(tool_call)
                        tool_outputs.append(
                            ToolOutput(
                                tool_call_id=tool_call.id,
                                output=output,
                            )
                        )
                    except Exception as e:
                        print(f"Error executing tool_call {tool_call.id}: {e}")

            print(f"Tool outputs: {tool_outputs}")
            if tool_outputs:
                await self.project_client.agents.submit_tool_outputs_to_stream(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                    event_handler=self,
                )

    async def on_run_step(self, step: "RunStep") -> None:
        await self.add_message(step)

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    async def execute_tool_call(self, tool_call: RequiredFunctionToolCall) -> Any:
        function_name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}") from e

        if function_name not in self.tools:
            raise ValueError(f"Function {function_name} not found in tools.")

        function = self.tools[function_name]
        if not inspect.iscoroutinefunction(function.func):
            raise ValueError(f"Function {function_name} is not a coroutine function (or awaitable).")

        arguments["notify"] = self.notify
        # Implement the logic to execute the tool call here
        # This is a placeholder implementation and should be replaced with actual logic
        print(f"Executing tool call: {tool_call.id}")
        # Simulate some processing time
        # await asyncio.sleep(1)
        return await function.func(**arguments)
