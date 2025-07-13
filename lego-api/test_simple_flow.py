from semantic_kernel.connectors.mcp import MCPStdioPlugin
from robot.robot_agent_orchestrator import LegoOrchestratorAgent
from robot.robot_agent_observer import LegoObserverAgent
from robot.robot_agent_planner import LegoPlannerAgent
from robot.robot_agent_controller import LegoControllerAgent
from robot.robot_agent_judger import LegoJudgerAgent
import asyncio
import shared
import json

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

    legoObserverAgent = LegoObserverAgent()
    legoControllerAgent = LegoControllerAgent()
    legoPlannerAgent = LegoPlannerAgent()
    await legoObserverAgent.init()
    await legoPlannerAgent.init()
    await legoControllerAgent.init()

    print("\033[93m \r\n-------- run_step1 -------- \033[0m")
    await legoObserverAgent.exec(
'''
describe the current field. blue object is robot, red object is goal.
'''
    )

    print("\033[93m \r\n-------- run_step2 -------- \033[0m")
    fielddata = shared.robotData.step1_analyze_json_data()
    controlldata = await legoPlannerAgent.exec(
'''
move robot forward to the red object and stop.
''' + fielddata
    )
    print("\033[93m \r\n-------- run_step3 -------- \033[0m")
    await legoControllerAgent.exec(
'''
Follow the plan to make robot action.
''' + controlldata
    )
    
    await shared.mcprobot.close()

if __name__ == "__main__":
    asyncio.run(main())

