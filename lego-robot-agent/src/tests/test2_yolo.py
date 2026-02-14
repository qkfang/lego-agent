"""Test script for observer agent using Microsoft Agent Framework."""
from lego_robot_agent.agents import (
    LegoOrchestratorAgent,
    LegoObserverAgent,
    LegoPlannerAgent,
    LegoControllerAgent,
    LegoJudgeAgent
)
from lego_robot_agent.type.models import FieldData
from lego_robot_agent.context import AgentContext
import asyncio
import lego_robot_agent.shared as shared
import json

async def main():
    try:
        shared.isTest = False
        shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework

        # Create context for the agent
        context = AgentContext(
            azure_client=shared.azure_client,
            mcp_session=None,
            mcp_legorobot_action=[],
        )

        legoObserverAgent = LegoObserverAgent()
        await legoObserverAgent.init(context)
        
        response = await legoObserverAgent.agent.run(
'''
describe the current field. blue object is robot, red object is goal.
''',
            response_format=FieldData
        )
        print(f"# {legoObserverAgent.AGENT_NAME}: {response}")
        field_data = response.value if hasattr(response, 'value') else None
        print(f"Structured output: {field_data}")
    finally:
        # Close Azure clients to prevent resource leaks
        if hasattr(shared.project_client, 'close'):
            await shared.project_client.close()
        if hasattr(shared.azure_client, 'close'):
            await shared.azure_client.close()

if __name__ == "__main__":
    asyncio.run(main())

