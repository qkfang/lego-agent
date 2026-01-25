"""Test script for observer agent using Microsoft Agent Framework."""
from lego_robot_agent.agents import (
    LegoOrchestratorAgent,
    LegoObserverAgent,
    LegoPlannerAgent,
    LegoControllerAgent,
    LegoJudgerAgent
)
import asyncio
import lego_robot_agent.shared as shared
import json

async def main():

    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework

    legoObserverAgent = LegoObserverAgent()
    await legoObserverAgent.init()
    await legoObserverAgent.exec(
'''
describe the current field. blue object is robot, red object is goal.
'''
    )

if __name__ == "__main__":
    asyncio.run(main())

