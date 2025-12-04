import asyncio
import shared
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from robot.robot_agent import LegoAgent

async def main():

    shared.isTest = False
    shared.foundryAgents = (await shared.project_client.agents.list_agents(limit=100)).data
    shared.mcprobot = MCPStdioPlugin(
            name="robotmcp",
            description="LEGO Robot Control Service",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\build\\index.js"],
            env={
                "PROJECT_CONNECTION_STRING": "",
                "DEFAULT_ROBOT_ID": "robot_b"
            },
        )
    await shared.mcprobot.connect()
    
    legoAgent = LegoAgent()

    await legoAgent.init()
    await legoAgent.robot_agent_run('grab bowser a coke and go back.')
    
    await shared.mcprobot.close()



if __name__ == "__main__":
    asyncio.run(main())


