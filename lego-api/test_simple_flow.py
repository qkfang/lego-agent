from semantic_kernel.connectors.mcp import MCPStdioPlugin
import asyncio
import shared
from robot.robot_simple import robot_agent_run_simple

async def main():
    shared.isTest = True
    shared.mcp = MCPStdioPlugin(
            name="robotmcp",
            description="Al Foundry Agents and run query, call this plugin.",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\build\\index.js"],
            env={
                "PROJECT_CONNECTION_STRING": "",
                "DEFAULT_ROBOT_ID": "robot_b"
            },
        )
    await shared.mcp.connect()
    
    await robot_agent_run_simple('robot to grab red object and move back 10 cm', None)
    
    await shared.mcp.close()

if __name__ == "__main__":
    asyncio.run(main())

