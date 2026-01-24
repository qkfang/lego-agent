"""Test script for multi-agent workflow using Microsoft Agent Framework."""
import asyncio
import lego_robot_agent.shared as shared
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from lego_robot_agent import LegoAgent
from lego_robot_agent.context import AgentContext
from lego_robot_agent.util.mcp_tools import wrap_mcp_tools

async def main():

    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework
    
    # Setup MCP connection
    mcp_server_params = StdioServerParameters(
        command="node",
        args=["c:\\repo\\lego-agent\\lego-mcp\\build\\index.js"],
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
                        
            # Create context for the agent
            context = AgentContext(
                azure_client=shared.azure_client,
                mcp_session=session,
                mcp_tools=shared.robotmcptools,
            )

            legoAgent = LegoAgent(context)

            await legoAgent.init()
            await legoAgent.run('grab bowser a coke and go back.')


if __name__ == "__main__":
    asyncio.run(main())


