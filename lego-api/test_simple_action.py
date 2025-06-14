from semantic_kernel.connectors.mcp import MCPStdioPlugin
from robot.robot_agent_controller import LegoControllerAgent
import asyncio
import shared

async def main():
    shared.isTest = False
    shared.foundryAgents = (await shared.project_client.agents.list_agents(limit=100)).data
    shared.mcprobot = MCPStdioPlugin(
            name="robotmcp",
            description="LEGO Robot Control Service",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\build\\index.js"],
            env={},
        )
    await shared.mcprobot.connect()

    legoControllerAgent = LegoControllerAgent()
    
    await legoControllerAgent.init()
    await legoControllerAgent.exec('move robot forward 30 cm')
    
    await shared.mcprobot.close()

if __name__ == "__main__":
    asyncio.run(main())

