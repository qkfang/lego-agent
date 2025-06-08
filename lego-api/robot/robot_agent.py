from robot.objectdetector import run 
from robot.robotmodel import RobotData, RoboProcessArgs
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents import AuthorRole
from robot.robot_agent_orchestrator import run_step0
from robot.robot_agent_observer import run_step1
from robot.robot_agent_planner import run_step2
from robot.robot_agent_controller import run_step3
from robot.robot_agent_judger import run_step4
from model import AgentUpdateEvent, Content
import shared
from shared import robotData
import os
import asyncio

async def monitor_temp_folder(temp_folder: str, notify: AgentUpdateEvent, callback=None, poll_interval: float = 2.0):
    """Monitor the temp folder for new files and call the callback with the new file name."""
    seen_files = set(os.listdir(temp_folder)) if os.path.exists(temp_folder) else set()
    while True:
        await asyncio.sleep(poll_interval)
        if not os.path.exists(temp_folder):
            continue
        current_files = set(os.listdir(temp_folder))
        new_files = current_files - seen_files
        if new_files:
            for f in new_files:
                await notify(
                    id="lego-controller",
                    subagent = "lego-controller",
                    status="robot actioned",
                    information= f,
                )

        seen_files = current_files



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
            # Check for 'goal completed' in the last 4 history entries
            return any(
                "goal completed" in h.content.lower() for h in history[-4:]
            )

    # 5. Place the agents in a group chat with a custom termination strategy
    chat = AgentGroupChat(
        agents=[agentOrchestrator, agentObserver, agentPlanner, agentController, agentJudger],
        termination_strategy=ApprovalTerminationStrategy(agents=[agentJudger], maximum_iterations=10),
    )
    shared.chat = chat
    shared.notify = notify

    temp_folder = os.path.join('D:/gh-repo/lego-agent/lego-mcp/temp')
    monitor_task = asyncio.create_task(monitor_temp_folder(temp_folder, notify))

    try:

        await chat.add_chat_message(message=goal)
        print(f"# {AuthorRole.USER}: '{goal}'")


        async for content in chat.invoke():
            print(f"\033[93m \r\n--------------------- {content.role} - {content.name or '*'} --------------------- \033[0m")
            print(f"{content.content}")

            if not notify is None:
                if content.name == "lego-observer" and robotData.field_data is not None and "blob" in robotData.field_data :
                    await notify(
                        id="image_update",
                        subagent = content.name,
                        status="field analysis completed",
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
                        status="responded",
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
        monitor_task.cancel()
        await chat.reset()
        

        await shared.project_client.agents.delete_agent(agentOrchestrator.id)
        await shared.project_client.agents.delete_agent(agentObserver.id)
        await shared.project_client.agents.delete_agent(agentPlanner.id)
        await shared.project_client.agents.delete_agent(agentController.id)
        await shared.project_client.agents.delete_agent(agentJudger.id)

    return "Robot agent run completed."