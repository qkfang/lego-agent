from robot.objectdetector import run 
from robot.robotmodel import RobotData, RoboProcessArgs
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents import AuthorRole
from robot.test_s0_orchestrator import run_step0
from robot.test_s1_observer import run_step1
from robot.test_s2_planner import run_step2
from robot.test_s3_controller import run_step3
from robot.test_s4_judger import run_step4
from model import AgentUpdateEvent, Content
import shared
from shared import robotData

async def robot_agent_run(goal: str, notify: AgentUpdateEvent):
  
    await shared.mcp.connect()

    agentOrchestrator = await run_step0(agentOnly=True)
    agentObserver = await run_step1(agentOnly=True)
    agentPlanner = await run_step2(agentOnly=True)
    agentController = await run_step3(agentOnly=True)
    agentJudger = await run_step4(agentOnly=True)

    class ApprovalTerminationStrategy(TerminationStrategy):
        """A strategy for determining when an agent should terminate."""

        async def should_agent_terminate(self, agent, history):
            """Check if the agent should terminate."""
            return "goal completed" in history[-1].content.lower()

    # 5. Place the agents in a group chat with a custom termination strategy
    chat = AgentGroupChat(
        agents=[agentOrchestrator, agentObserver, agentPlanner, agentController, agentJudger],
        termination_strategy=ApprovalTerminationStrategy(agents=[agentJudger], maximum_iterations=10),
    )
    shared.chat = chat

    try:

        await chat.add_chat_message(message=goal)
        print(f"# {AuthorRole.USER}: '{goal}'")
        async for content in chat.invoke():
            print("\033[93m \r\n--------------------- agent --------------------- \033[0m")
            print(f"# {content.role} - {content.name or '*'}: '{content.content}'")

            if notify != None:
                await notify(
                    id=content.name,
                    status="run done",
                    information=content.content,
                )

            if content.name == "lego-observer":
                await notify(
                    id="image_edit",
                    subagent = content.name,
                    status="step_completed",
                    content=Content(
                        type="image",
                        content=[
                            {
                                "type": "image",
                                "description": content.content,
                                "image_url": robotData.field_data["blob"],
                                "kind": 'image',
                            }
                        ],
                    ),
                    output=True,
                )
            else:
                await notify(
                    id="text_update",
                    subagent = content.name,
                    status="step_completed",
                    content=Content(
                        type="text",
                        content=[
                            {
                                "type": "text",
                                "value": content.content,
                            }
                        ],
                    ),
                    output=True,
                )
        

    finally:
        await chat.reset()
        
        await shared.project_client.agents.delete_agent(agentOrchestrator.id)
        await shared.project_client.agents.delete_agent(agentObserver.id)
        await shared.project_client.agents.delete_agent(agentPlanner.id)
        await shared.project_client.agents.delete_agent(agentController.id)
        await shared.project_client.agents.delete_agent(agentJudger.id)
