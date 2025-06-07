from dataclasses import asdict
from typing import Any
from fastapi import APIRouter
from fastapi.websockets import WebSocketState
from pydantic import BaseModel
from agent.common import execute_foundry_agent, post_request

from agent.decorators import function_agents, function_calls
from model import Agent, AgentUpdate, AgentUpdateEvent, Content
from openai.types.beta.realtime import (
    SessionUpdateEvent,
    InputAudioBufferAppendEvent,
    # InputAudioBufferCommitEvent,
    # InputAudioBufferClearEvent,
    ConversationItemCreateEvent,
    # ConversationItemTruncateEvent,
    # ConversationItemDeleteEvent,
    ResponseCreateEvent,
    ConversationItem
    # ResponseCancelEvent,
)

from agent.common import (
    get_client_agents,
    get_foundry_agents,
    get_custom_agents,
    custom_agents,
    foundry_agents,
)

import json
import shared
import agent.agents as agents  # noqa: F401
import agent.functions as functions  # noqa: F401
from connection import connections
# from . import robot_mcp_agent


# available agents
router = APIRouter(
    prefix="/api/agent",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


@router.get("/refresh")
async def refresh_agents():
    # reload agents from prompty files in directory
    await get_custom_agents()
    return {"message": "Agents refreshed"}


@router.get("/")
async def get_agents():
    global connections, custom_agents, foundry_agents, function_agents
    if not custom_agents:
        await get_custom_agents()
    # return list of available agents
    a = [
        Agent(
            id=agent.id,
            name=agent.name,
            type=agent.model.connection["type"],
            description=agent.description,
            options=agent.model.options,
            parameters=[
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                for param in agent.inputs
            ],
        )
        for agent in custom_agents.values()
    ]
    agents = await get_foundry_agents()
    f = [
        Agent(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            description=agent.description,
            parameters=[
                {
                    "name": param["name"],
                    "type": param["type"],
                    "description": param["description"],
                    "required": param["required"],
                }
                for param in agent.parameters
            ],
        )
        for agent in agents.values()
    ]

    return [*f, *a, *function_agents.values(), *get_client_agents().values()]


@router.get("/function")
async def get_functions():
    global function_calls
    return [asdict(f) for f in function_calls.values()]


@router.get("/{id}")
async def get_agent(id: str):
    global connections, custom_agents, foundry_agents
    # return agent by id
    if id not in custom_agents:
        return {"error": "Agent not found"}

    return {k: v for k, v in custom_agents[id].to_safe_dict().items() if k != "file"}


def send_agent_status(connection_id: str, name: str, call_id: str) -> AgentUpdateEvent:
    global connections

    async def send_status(
        id: str,
        status: str,
        subagent: str | None = None,
        information: str | None = None,
        content: Content | None = None,
        output: bool = False,
    ):
        # send agent status to connection
        if (
            connection_id in connections
            and connections[connection_id].state == WebSocketState.CONNECTED
        ):
            await connections[connection_id].send_browser_update(
                AgentUpdate(
                    id=id,
                    type="agent",
                    call_id=call_id,
                    name=subagent if subagent is not None else name,
                    status=status,
                    information=information,
                    content=content,
                    output=output,
                )
            )
        else:
            # connection is closed, remove agent from connections
            if connection_id in connections:
                connections.remove(connection_id)
                print(f"Connection {connection_id} is closed, removing connection")
            # print notifications to console
            print(f"Agent {name} ({id}) - {status}")

    # return status function
    return send_status


class FunctionCall(BaseModel):
    call_id: str
    id: str
    name: str
    arguments: dict[str, Any]



@router.post("/{id}")
async def execute_agent(id: str, function: FunctionCall):
    global connections, custom_agents, foundry_agents, function_agents, function_calls

    if len(foundry_agents) == 0:
        foundry_agents = await get_foundry_agents()

    if id not in connections:
        return {"error": "Connection not found"}
    
    print(f"Executing agent {id} with function {function.name} and arguments {function.arguments}")
    
    if function.name.startswith("xxx"):
        cmd = "perform below action: " +  function.name + " " + json.dumps(function.arguments) + " "
        await robot_mcp_agent.run(cmd, shared.mcp)
    elif function.name in foundry_agents:
        # execute foundry agent
        foundry_agent = foundry_agents[function.name]
        await execute_foundry_agent(
            foundry_agent.id,
            function.arguments["additional_instructions"],
            function.arguments["query"],
            function_calls,
            send_agent_status(
                connection_id=id, name=foundry_agent.name, call_id=function.call_id
            ),
        )
    elif function.name in function_agents:
        function_agent = function_agents[function.name]
        functions = dir(agents)
        if function_agent.id in functions:
            # execute function agent
            func = getattr(agents, function_agent.id)
            args = function.arguments.copy()
            args["notify"] = send_agent_status(
                connection_id=id, name=function_agent.name, call_id=function.call_id
            )
            result = await func(**args)

            # await shared.realtime1.realtime.send(
            #     ConversationItemCreateEvent(
            #         type="conversation.item.create",
            #         item=ConversationItem(
            #             call_id=function.call_id,
            #             type="function_call_output",
            #             output= json.dumps(result , indent=2)
            #         ),
            #     )
            # )
        else:
            return {"error": "Function not found"}
    
    return {
        "message": f"Agent {function.name} executed",
        "call_id": function.call_id,
    }
