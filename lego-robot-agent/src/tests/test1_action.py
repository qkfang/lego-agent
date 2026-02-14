"""Test script for robot controller agent using Microsoft Agent Framework."""

from agent_framework import MCPStdioTool
from lego_robot_agent.agents import LegoControllerAgent
from lego_robot_agent.context import AgentContext
import asyncio
import lego_robot_agent.shared as shared

async def main():
    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]
    
    # Setup MCP connection using Microsoft Agent Framework's MCPStdioTool
    mcp_tool = MCPStdioTool(
        name="robot_mcp",
        command="node",
        args=[shared.mcp_server_path],
        env={"IS_MOCK": "true"},
    )
    
    # Create context for the agent
    context = AgentContext(
        azure_client=shared.azure_client,
        mcp_session=None,  # Not needed with MCPStdioTool
        mcp_tools=[mcp_tool],  # Pass the MCP tool directly
        robot_data=shared.robotData,
        is_test=True
    )
    
    legoControllerAgent = LegoControllerAgent()
    
    await legoControllerAgent.init(context)
    await legoControllerAgent.exec('move robot forward 10cm')

if __name__ == "__main__":
    asyncio.run(main())

