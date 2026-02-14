"""
Test script demonstrating the refactored LegoAgent with dependency injection.

This test uses the new lego-robot-agent package with AgentContext
instead of relying on global shared state.
"""

import asyncio
from agent_framework import MCPStdioTool

# New import style using the refactored package
from lego_robot_agent import LegoAgent, AgentContext, RobotData
import lego_robot_agent.shared as shared


async def main():
    """Run the LegoAgent with a sample goal."""
    
    # Setup MCP connection using Microsoft Agent Framework's MCPStdioTool
    mcp_tool = MCPStdioTool(
        name="robot_mcp",
        command="node",
        args=[shared.mcp_server_path],
        env={
            "PROJECT_CONNECTION_STRING": "",
            "DEFAULT_ROBOT_ID": "robot_b"
        },
        load_prompts=False,  # lego-mcp doesn't implement prompts
    )
    
    # Create the agent context with all dependencies
    context = AgentContext(
        azure_client=shared.azure_client,
        mcp_session=None,  # Not needed with MCPStdioTool
        mcp_legorobot_action=[mcp_tool],  # Pass the MCP tool directly
        robot_data=RobotData(),
        is_test=True,  # Use test images
        test_count=1,
    )
    
    # Optional: Add notification callback
    async def notify_callback(**kwargs):
        print(f"[NOTIFY] {kwargs.get('subagent')}: {kwargs.get('status')}")
    
    context.notify_callback = notify_callback
    
    # Create and initialize the agent
    agent = LegoAgent(context)
    await agent.init()
    
    # Run the agent with a goal
    result = await agent.run("Pick up the coke and deliver it to Bowser")
    print(f"\n{result}")


if __name__ == "__main__":
    asyncio.run(main())
