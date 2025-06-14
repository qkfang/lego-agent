from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents import AuthorRole
from robot.robot_agent_orchestrator import LegoOrchestratorAgent
from robot.robot_agent_observer import LegoObserverAgent
from robot.robot_agent_planner import LegoPlannerAgent
from robot.robot_agent_controller import LegoControllerAgent
from robot.robot_agent_judger import LegoJudgerAgent
from model import AgentUpdateEvent, Content
import shared
import os
import asyncio


class LegoAgent:

    legoOrchestratorAgent = LegoOrchestratorAgent()
    legoObserverAgent = LegoObserverAgent()
    legoPlannerAgent = LegoPlannerAgent()
    legoControllerAgent = LegoControllerAgent()
    legoJudgerAgent = LegoJudgerAgent()
    init_done = False


    async def init(self):
        if(not self.init_done):
            await self.legoOrchestratorAgent.init()
            await self.legoObserverAgent.init()
            await self.legoPlannerAgent.init()
            await self.legoControllerAgent.init()
            await self.legoJudgerAgent.init()
            self.init_done = True



    async def monitor_temp_folder(self, temp_folder: str, callback=None, poll_interval: float = 2.0):
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
                    await shared.notify(
                        id="lego-controller",
                        subagent = "lego-controller",
                        status="robot actioned",
                        information= f,
                    )

            seen_files = current_files


    async def robot_agent_run(self, goal: str):
        await shared.mcprobot.connect()

        class ApprovalTerminationStrategy(TerminationStrategy):
            """A strategy for determining when an agent should terminate."""

            async def should_agent_terminate(self, agent, history):
                """Check if the agent should terminate."""
                # Check for 'goal completed' in the last 4 history entries
                return any(
                    "goal completed" in h.content.lower() for h in history[-4:]
                )

        shared.chat = AgentGroupChat(
            agents=[self.legoOrchestratorAgent.agent, self.legoObserverAgent.agent, self.legoPlannerAgent.agent, self.legoControllerAgent.agent, self.legoJudgerAgent.agent],

            termination_strategy=ApprovalTerminationStrategy(agents=[self.legoJudgerAgent.agent], maximum_iterations=10),
        )

        
        temp_folder = os.path.join('D:/gh-repo/lego-agent/lego-mcp/temp')
        monitor_task = asyncio.create_task(self.monitor_temp_folder(temp_folder))

        try:

            await shared.chat.add_chat_message(message=goal)
            print(f"# {AuthorRole.USER}: '{goal}'")

            async for content in shared.chat.invoke():
                print(f"\033[93m \r\n--------------------- {content.role} - {content.name or '*'} --------------------- \033[0m")
                print(f"{content.content}")

                if not shared.notify is None:
                    if content.name == "lego-observer" and shared.robotData.field_data is not None and "blob" in shared.robotData.field_data :
                        await shared.notify(
                            id="image_update",
                            subagent = content.name,
                            status="field analysis completed",
                            content=Content(
                                type="image",
                                content=[
                                    {
                                        "type": "image",
                                        "description": content.content,
                                        "image_url": shared.robotData.field_data["blob"],
                                        "kind": 'image',
                                    }
                                ],
                            ),
                            output=True,
                        )
                    else:
                        await shared.notify(
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
            await shared.chat.reset()
        
        return "Robot agent run completed."