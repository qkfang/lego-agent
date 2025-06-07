import asyncio
import shared
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from agent.agents import robot_agent_run


async def main():
      
    shared.mcp = MCPStdioPlugin(
            name="robotmcp",
            description="Al Foundry Agents and run query, call this plugin.",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\typescript\\build\\index.js"],
            env={
                "PROJECT_CONNECTION_STRING": "",
                "DEFAULT_ROBOT_ID": "robot_b"
            },
        )
    
    await robot_agent_run('ask robot to grab the red object and go home', None)



if __name__ == "__main__":
    asyncio.run(main())


