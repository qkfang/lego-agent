"""Test script for sequential agent workflow using Microsoft Agent Framework."""
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from lego_robot_agent.agents import (
    LegoOrchestratorAgent,
    LegoObserverAgent,
    LegoPlannerAgent,
    LegoControllerAgent,
    LegoJudgerAgent
)
from lego_robot_agent.util.mcp_tools import wrap_mcp_tools
import asyncio
import lego_robot_agent.shared as shared
import json

async def main():

    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework
    
    # Setup MCP connection
    mcp_server_params = StdioServerParameters(
        command="node",
        args=[shared.mcp_server_path],
        env={},
    )
    
    async with stdio_client(mcp_server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            shared.mcprobot = session
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools if hasattr(tools_result, 'tools') else []
            # Wrap MCP tools to make them callable for agent framework
            shared.robotmcptools = wrap_mcp_tools(mcp_tools, session)

            legoObserverAgent = LegoObserverAgent()
            legoControllerAgent = LegoControllerAgent()
            legoPlannerAgent = LegoPlannerAgent()
            await legoObserverAgent.init()
            await legoPlannerAgent.init()
            await legoControllerAgent.init()

            print("\033[93m \r\n-------- run_step1 -------- \033[0m")
            await legoObserverAgent.exec(
'''
describe the current field. blue object is robot, red object is goal.
'''
            )

            print("\033[93m \r\n-------- run_step2 -------- \033[0m")
            fielddata = shared.robotData.step1_analyze_json_data()
            controlldata = await legoPlannerAgent.exec(
'''
move robot forward to the coke, and grab it.
''' + fielddata
            )
            
            print("\033[93m \r\n-------- run_step3 -------- \033[0m")
            await legoControllerAgent.exec(
'''
Follow the plan to make robot action.
''' + controlldata
            )

if __name__ == "__main__":
    asyncio.run(main())

