"""Test script for multi-agent workflow using Microsoft Agent Framework."""
import asyncio
import lego_robot_agent.shared as shared
from agent_framework import MCPStdioTool
from lego_robot_agent import LegoAgent
from lego_robot_agent.context import AgentContext

async def main():

    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework
    
    # Setup MCP connection using Microsoft Agent Framework's MCPStdioTool
    mcp_tool = MCPStdioTool(
        name="robot_mcp",
        command="node",
        args=[shared.mcp_server_path],
        env={},
    )
    
    # Create context for the agent
    context = AgentContext(
        azure_client=shared.azure_client,
        mcp_session=None,  # Not needed with MCPStdioTool
        mcp_tools=[mcp_tool],  # Pass the MCP tool directly
        robot_data=shared.robotData,
        is_test=True
    )

    legoAgent = LegoAgent(context)

    await legoAgent.init()
    await legoAgent.run('grab bowser a coke and go back.')


if __name__ == "__main__":
    asyncio.run(main())


