"""Test script for sequential agent workflow using Microsoft Agent Framework."""
from agent_framework import MCPStdioTool
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
    
    async with MCPStdioTool(
        name="robot_mcp",
        command="node",
        args=[shared.mcp_server_path],
        env={"IS_MOCK": "true"},
        load_prompts=False,
    ) as mcp_tool:
        # Create context for the agents
        context = AgentContext(
            azure_client=shared.azure_client,
            mcp_session=None, 
            mcp_legorobot_action=[mcp_tool],
            robot_data=shared.robotData,
            is_test=False
        )

        legoObserverAgent = LegoObserverAgent()
        legoControllerAgent = LegoControllerAgent()
        legoPlannerAgent = LegoPlannerAgent()
        await legoObserverAgent.init(context)
        await legoPlannerAgent.init(context)
        await legoControllerAgent.init(context)

        print("\033[93m \r\n-------- run_step1 -------- \033[0m")
        await legoObserverAgent.exec(
    '''
    describe the current field. blue object is robot, red object is coke.
    '''
        )

        print("\033[93m \r\n-------- run_step2 -------- \033[0m")
        fielddata = shared.robotData.step1_analyze_json_data()
        controlldata = await legoPlannerAgent.exec(
    '''
    move robot forward to the coke.
    ''' + fielddata
        )
        
        print("\033[93m \r\n-------- run_step3 -------- \033[0m")
        await legoControllerAgent.exec(
    '''
    Follow the plan to make robot action.
    ''' + controlldata
        )
        
        # Clean up Azure client resources
        for agent in [legoObserverAgent, legoControllerAgent, legoPlannerAgent]:
            if hasattr(agent.agent, 'chat_client'):
                await agent.agent.chat_client.close()
    
    # Clean up project client
    await shared.project_client.close()

if __name__ == "__main__":
    asyncio.run(main())

