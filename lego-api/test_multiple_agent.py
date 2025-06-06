import asyncio
import shared
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from agent.agents import robot_agent_run


async def main():
      
    lego_robot_mcp = MCPStdioPlugin(
            name="AIFoundryAgents",
            description="Al Foundry Agents and run query, call this plugin.",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\typescript\\build\\index.js"],
            env={
                "PROJECT_CONNECTION_STRING": "eastus2.api.azureml.ms;79b9afaa-2d77-4d1e-b902-98df2bd3b3d6;rg-agent100;mamimezf5xgqov-aiproject",
                "DEFAULT_ROBOT_ID": "robot_b"
            },
        )
    await lego_robot_mcp.connect()
    
    shared.mcp = lego_robot_mcp
    await robot_agent_run('move robot to the red object', None)



if __name__ == "__main__":
    asyncio.run(main())


