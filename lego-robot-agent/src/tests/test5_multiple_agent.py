"""Test script for multi-agent workflow using Microsoft Agent Framework."""
import asyncio
import lego_robot_agent.shared as shared
from agent_framework import MCPStdioTool
from lego_robot_agent import LegoAgent
from lego_robot_agent.context import AgentContext

async def main():

    shared.isTest = True
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]  # Agents are created on-demand in new framework
    
    # Use async with context manager for proper resource cleanup
    # Following the pattern from:
    # https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/mcp/mcp_api_key_auth.py
    async with MCPStdioTool(
        name="robot_mcp",
        command="node",
        args=[shared.mcp_server_path],
        env={"IS_MOCK": "true"},
        load_prompts=False,  # lego-mcp doesn't implement prompts
    ) as mcp_tool:
        # Create context for the agent
        context = AgentContext(
            azure_client=shared.azure_client,
            mcp_session=None,  # Not needed with MCPStdioTool
            mcp_legorobot_action=[mcp_tool],  # Pass the MCP tool directly
            robot_data=shared.robotData,
            is_test=True
        )

        legoAgent = LegoAgent(context)

        await legoAgent.init()
        await legoAgent.run('grab bowser a coke and go back.')
        
        # Clean up Azure client resources for all sub-agents
        for agent in [legoAgent._orchestrator, legoAgent._observer, legoAgent._planner, 
                      legoAgent._controller, legoAgent._judge]:
            if hasattr(agent, 'agent') and hasattr(agent.agent, 'chat_client'):
                await agent.agent.chat_client.close()
    
    # Clean up project client
    await shared.project_client.close()


if __name__ == "__main__":
    asyncio.run(main())


