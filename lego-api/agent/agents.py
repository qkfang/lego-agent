import os
import io
import base64
import json
import aiohttp
# Temporarily disable due to agent_framework compatibility
# import lego_robot_agent.shared as lego_shared
# from lego_robot_agent.util.storage import save_image_blobs, save_image_binary_blobs
# from lego_robot_agent import RobotData, RoboProcessArgs
# from lego_robot_agent import LegoAgent, AgentContext
from typing import Annotated
from agent.decorators import agent
from model import AgentUpdateEvent, Content
from agent.common import execute_foundry_agent, post_request
from dotenv import load_dotenv
load_dotenv()

AZURE_IMAGE_ENDPOINT = os.environ.get("AZURE_IMAGE_ENDPOINT", "EMPTY").rstrip("/")
AZURE_IMAGE_API_KEY = os.environ.get("AZURE_IMAGE_API_KEY", "EMPTY")

# LegoAgent is temporarily disabled due to agent_framework compatibility
# legoAgent: LegoAgent = None


# def _get_lego_agent() -> LegoAgent:
#     """Get or create the LegoAgent with context from shared module."""
#     global legoAgent
#     if legoAgent is None:
#         context = AgentContext(
#             azure_client=lego_shared.azure_client,
#             mcp_session=lego_shared.mcprobot,
#             mcp_tools=lego_shared.robotmcptools,
#             robot_data=lego_shared.robotData,
#             is_test=lego_shared.isTest,
#             test_count=lego_shared.isTestCount,
#         )
#         legoAgent = LegoAgent(context)
#     return legoAgent

@agent(
    name="Robot Agent",
    description='''
    This robot agent can control robot to perform a goal. while robot is performing the action, you need to wait for the robot to complete the action before continue the conversation.
    ''',
)
async def robot_agent(
    goal: Annotated[
        str,
        "The goal that the robot should achieve. This can be a simple task or a complex goal that requires multiple steps to complete.",
    ],
    notify: AgentUpdateEvent,
) -> list[str]:
    # Temporarily disabled due to agent_framework compatibility
    # agent = _get_lego_agent()
    # agent.context.notify_callback = notify
    # await agent.init()
    # await agent.run(goal)
    
    # For testing purposes, just log the goal
    print(f"Robot agent called with goal: {goal}")
    await notify("robot_agent", "running", information=f"Processing goal: {goal}")
    await notify("robot_agent", "completed", information="Robot agent execution completed (stub)", output=True)
        
    return [f"Robot agent stub completed. Goal was: {goal}"]
