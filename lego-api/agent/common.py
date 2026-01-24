import os
import aiohttp
import prompty
from prompty.tracer import trace
import contextlib
from pathlib import Path
from typing import AsyncGenerator, Union, Unpack, Any
from aiohttp.client import _RequestOptions

from azure.identity.aio import DefaultAzureCredential
from prompty.core import Prompty

from model import Agent, AgentUpdateEvent, Function

from dotenv import load_dotenv

load_dotenv()

# Microsoft Agent Framework configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

foundry_agents: dict[str, Agent] = {}
custom_agents: dict[str, Prompty] = {}


# load agents from prompty files in directory
async def get_custom_agents() -> dict[str, Prompty]:
    global custom_agents
    agents_dir = Path(__file__).parent / "prompty"
    if not agents_dir.exists():
        # print(f"No custom agents found in {agents_dir}")
        return {}

    custom_agents.clear()
    for agent_file in agents_dir.glob("*.prompty"):
        agent_name = agent_file.stem
        prompty_agent = await prompty.load_async(str(agent_file))
        custom_agents[prompty_agent.id] = prompty_agent
        print(f"Loaded agent: {agent_name}")

    return custom_agents


def get_client_agents() -> dict[str, Agent]:
    # selection_agent = Agent(
    #    id="client_image_selection",
    #    name="Client Image Selection Task",
    #    type="client-agent",
    #    description="If the user needs to provide an image, call this agent to select the image. This agent will return the selected image.",
    #    parameters=[
    #        {
    #            "name": "image",
    #            "type": "string",
    #            "description": "The exact imnage url selected by the user. Use whatever is returned EXACTLY as it is.",
    #            "required": True,
    #        },
    #    ],
    # )

    return {
        # "selection_agent": selection_agent,
    }


async def get_available_agents() -> dict[str, Agent]:
    """Get available agents - simplified for Microsoft Agent Framework.
    
    In the new framework, agents are created on-demand rather than 
    pre-registered in a service. This function returns configured agents.
    """
    global foundry_agents
    
    # Return cached agents or empty dict
    # Agents are now created directly in the robot agent files
    return foundry_agents


@trace
async def execute_agent(
    agent_id: str,
    additional_instructions: str,
    query: str,
    tools: dict[str, Function],
    notify: AgentUpdateEvent,
):
    """Execute an agent using Microsoft Agent Framework.
    
    Note: This function is maintained for compatibility but the main
    agent execution now happens through the workflow in robot_agent.py
    """
    import shared
    
    # For now, log the execution request
    # The actual execution happens through the workflow
    print(f"Agent execution requested: {agent_id}")
    print(f"Query: {query}")
    print(f"Additional instructions: {additional_instructions}")


async def create_thread():
    """Create a new conversation thread.
    
    In Microsoft Agent Framework, threads are managed internally by agents
    or through workflow state. This is kept for compatibility.
    """
    import uuid
    # Generate a unique thread ID for tracking
    thread_id = str(uuid.uuid4())
    return thread_id


async def create_thread_message(
    thread_id: str,
    role: str,
    content: str,
    attachments: list = [],
    metadata: dict[str, str] = {},
):
    """Create a message in a thread.
    
    In Microsoft Agent Framework, messages are passed directly to agents.
    This is kept for compatibility.
    """
    import uuid
    message_id = str(uuid.uuid4())
    print(f"Thread message created: {message_id} in thread {thread_id}")
    return message_id


@contextlib.asynccontextmanager
async def post_request(
    url: str, **kwargs: Unpack[_RequestOptions]
) -> AsyncGenerator[dict[str, Any], None]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            if response.status != 200:
                state = await response.json()
                yield state
            else:
                response_data = await response.json()
                yield response_data
