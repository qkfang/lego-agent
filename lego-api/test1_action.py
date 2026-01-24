"""Test script for robot controller agent using Microsoft Agent Framework."""
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from robot.robot_agent_controller import LegoControllerAgent
from util.mcp_tools import wrap_mcp_tools
import asyncio
import shared

async def main():
    shared.isTest = False
    shared.foundryAgents = []  # Agents are created on-demand in new framework
    
    # Setup MCP connection
    mcp_server_params = StdioServerParameters(
        command="node",
        args=["c:\\repo\\lego-agent\\lego-mcp\\build\\index.js"],
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
            
            legoControllerAgent = LegoControllerAgent()
            
            await legoControllerAgent.init()
            await legoControllerAgent.exec('hi')

if __name__ == "__main__":
    asyncio.run(main())

