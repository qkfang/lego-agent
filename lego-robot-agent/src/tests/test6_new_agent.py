"""
Test script demonstrating the refactored LegoAgent with dependency injection.

This test uses the new lego-robot-agent package with AgentContext
instead of relying on global shared state.
"""

import asyncio
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

# New import style using the refactored package
from lego_robot_agent import LegoAgent, AgentContext, RobotData
from lego_api.util.mcp_tools import wrap_mcp_tools
from mcp_test_utils import get_mcp_server_path


async def main():
    """Run the LegoAgent with a sample goal."""
    
    # Get MCP server path
    mcp_server_path = get_mcp_server_path()
    
    # Setup MCP connection
    mcp_server_params = StdioServerParameters(
        command="node",
        args=[str(mcp_server_path)],
        env={
            "PROJECT_CONNECTION_STRING": "",
            "DEFAULT_ROBOT_ID": "robot_b"
        },
    )
    
    async with stdio_client(mcp_server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            await mcp_session.initialize()
            
            # Get MCP tools
            tools_result = await mcp_session.list_tools()
            mcp_tools = tools_result.tools if hasattr(tools_result, 'tools') else []
            wrapped_tools = wrap_mcp_tools(mcp_tools, mcp_session)
            
            # Create Azure client (import from shared for now)
            from lego_api.shared import azure_client
            
            # Create the agent context with all dependencies
            context = AgentContext(
                azure_client=azure_client,
                mcp_session=mcp_session,
                mcp_tools=wrapped_tools,
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
