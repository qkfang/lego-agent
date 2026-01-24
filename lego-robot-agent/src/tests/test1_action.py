"""Test script for robot controller agent using Microsoft Agent Framework."""
import sys
import os
from pathlib import Path

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from lego_robot_agent.agents import LegoControllerAgent
from lego_robot_agent.context import AgentContext
from lego_robot_agent.util.mcp_tools import wrap_mcp_tools
import asyncio
import lego_robot_agent.shared as shared
from mcp_test_utils import get_mcp_server_path

async def main():
    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]
    
    # Get MCP server path
    mcp_server_path = get_mcp_server_path()
    
    # Setup MCP connection
    mcp_server_params = StdioServerParameters(
        command="node",
        args=[str(mcp_server_path)],
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
            
            # Create context for the agent
            context = AgentContext(
                azure_client=shared.azure_client,
                mcp_session=session,
                mcp_tools=shared.robotmcptools,
            )
            
            legoControllerAgent = LegoControllerAgent()
            
            await legoControllerAgent.init(context)
            await legoControllerAgent.exec('hi. 1+1 = ?')

if __name__ == "__main__":
    asyncio.run(main())

