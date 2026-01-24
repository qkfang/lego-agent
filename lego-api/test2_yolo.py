"""Test script for observer agent using Microsoft Agent Framework."""
from robot.robot_agent_orchestrator import LegoOrchestratorAgent
from robot.robot_agent_observer import LegoObserverAgent
from robot.robot_agent_planner import LegoPlannerAgent
from robot.robot_agent_controller import LegoControllerAgent
from robot.robot_agent_judger import LegoJudgerAgent
import asyncio
import shared
import json

async def main():

    shared.isTest = False
    shared.foundryAgents = []  # Agents are created on-demand in new framework

    legoObserverAgent = LegoObserverAgent()
    await legoObserverAgent.init()
    await legoObserverAgent.exec(
'''
describe the current field. blue object is robot, red object is goal.
'''
    )

if __name__ == "__main__":
    asyncio.run(main())

