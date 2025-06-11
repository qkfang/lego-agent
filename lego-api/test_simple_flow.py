from semantic_kernel.connectors.mcp import MCPStdioPlugin
from robot.robot_agent_orchestrator import LegoOrchestratorAgent
from robot.robot_agent_observer import LegoObserverAgent
from robot.robot_agent_planner import LegoPlannerAgent
from robot.robot_agent_controller import LegoControllerAgent
from robot.robot_agent_judger import LegoJudgerAgent
import asyncio
import shared

async def main():
    shared.isTest = True
    shared.foundryAgents = (await shared.project_client.agents.list_agents(limit=100)).data
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

    legoOrchestratorAgent = LegoOrchestratorAgent()
    legoControllerAgent = LegoControllerAgent()
    legoJudgerAgent = LegoJudgerAgent()
    legoObserverAgent = LegoObserverAgent()
    legoPlannerAgent = LegoPlannerAgent()
    
    await legoOrchestratorAgent.init()
    await legoObserverAgent.init()
    await legoPlannerAgent.init()
    await legoControllerAgent.init()
    await legoJudgerAgent.init()

    print("\033[93m \r\n--------------------- run_step1 --------------------- \033[0m")
    await legoObserverAgent.run_step1()

    print("\033[93m \r\n--------------------- run_step2 --------------------- \033[0m")
    await legoPlannerAgent.run_step2()
    
    print("\033[93m \r\n--------------------- run_step3 --------------------- \033[0m")
    await legoControllerAgent.run_step3()

    # print("\033[93m \r\n--------------------- run_step1 --------------------- \033[0m")
    # await run_step1()
    # await run_step4()

    # print("\033[93m \r\n--------------------- run_step1 --------------------- \033[0m")
    # await run_step1()
    # await run_step4()
    
    await shared.mcp.close()

if __name__ == "__main__":
    asyncio.run(main())

