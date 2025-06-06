import asyncio

from model import AgentUpdateEvent
from agent.decorators import function

@function
async def example_function(param1: str, param2: int, notify: AgentUpdateEvent):
    await asyncio.sleep(1)  # Simulate some async work
    # Notify the agent about the update
    await notify(id="id", status="success")

    return param1 + str(param2)


@function
async def example_function_other(param1: str, param2: int, super_param33: bool, notify: AgentUpdateEvent):
    await asyncio.sleep(1)  # Simulate some async work
    # Notify the agent about the update
    await notify(id="id", status="success")

    return param1 + str(param2) + str(super_param33)
