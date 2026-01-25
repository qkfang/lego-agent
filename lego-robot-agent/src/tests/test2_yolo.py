"""Test script for observer agent using Microsoft Agent Framework."""
from lego_robot_agent.agents import (
    LegoOrchestratorAgent,
    LegoObserverAgent,
    LegoPlannerAgent,
    LegoControllerAgent,
    LegoJudgerAgent
)
from lego_robot_agent.context import AgentContext
import asyncio
import lego_robot_agent.shared as shared
import json

async def main():

    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework

    # Create context for the agent
    context = AgentContext(
        azure_client=shared.azure_client,
        mcp_session=None,
        mcp_tools=[],
    )

    legoObserverAgent = LegoObserverAgent()
    await legoObserverAgent.init(context)
    await legoObserverAgent.exec(
'''
describe the current field. blue object is robot, red object is goal.
'''
    )

if __name__ == "__main__":
    asyncio.run(main())

