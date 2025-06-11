import shared
from robot.objectdetector import run 
from robot.robotmodel import RobotData, RoboProcessArgs
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents import AuthorRole
from robot.robot_agent_orchestrator import LegoOrchestratorAgent
from robot.robot_agent_observer import LegoObserverAgent
from robot.robot_agent_planner import LegoPlannerAgent
from robot.robot_agent_controller import LegoControllerAgent
from robot.robot_agent_judger import LegoJudgerAgent
from model import AgentUpdateEvent, Content
from shared import robotData

async def robot_agent_run_simple(goal: str, notify: AgentUpdateEvent):
  
    await shared.mcp.connect()

    shared.foundryAgents = (await shared.project_client.agents.list_agents(limit=100)).data
    shared.isTest = True

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