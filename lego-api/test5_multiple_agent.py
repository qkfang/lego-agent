"""Test script for multi-agent workflow using Microsoft Agent Framework."""
import asyncio
import shared
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from robot.robot_agent import LegoAgent
from util.mcp_tools import wrap_mcp_tools

async def main():

    shared.isTest = False
    shared.foundryAgents = []  # Agents are created on-demand in new framework
    
    # Setup MCP connection
    mcp_server_params = StdioServerParameters(
        command="node",
        args=["D:\\gh-repo\\lego-agent\\lego-mcp\\build\\index.js"],
        env={
            "PROJECT_CONNECTION_STRING": "",
            "DEFAULT_ROBOT_ID": "robot_b"
        },
    )
    
    async with stdio_client(mcp_server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            shared.mcprobot = session
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools if hasattr(tools_result, 'tools') else []
            # Wrap MCP tools to make them callable for agent framework
            shared.robotmcptools = wrap_mcp_tools(mcp_tools, session)
            
            legoAgent = LegoAgent()

            await legoAgent.init()
            await legoAgent.robot_agent_run('grab bowser a coke and go back.')


if __name__ == "__main__":
    asyncio.run(main())


