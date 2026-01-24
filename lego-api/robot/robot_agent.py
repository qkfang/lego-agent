
from typing import ClassVar, List
from agent_framework import ChatAgent
from agent_framework.workflows import AgentWorkflowBuilder, GroupChatManager, WorkflowEvent
from agent_framework.workflows.orchestrations import RoundRobinGroupChatManager
from robot.robot_agent_orchestrator import LegoOrchestratorAgent
from robot.robot_agent_observer import LegoObserverAgent
from robot.robot_agent_planner import LegoPlannerAgent
from robot.robot_agent_controller import LegoControllerAgent
from robot.robot_agent_judger import LegoJudgerAgent
from model import AgentUpdateEvent, Content
import shared
import os
import asyncio


class LegoGroupChatManager(RoundRobinGroupChatManager):
    """Custom group chat manager for LEGO robot agents that follows a logical workflow."""
    
    def __init__(self, agents: List[ChatAgent]):
        super().__init__(agents)
        self.action_executing: bool = False
        self.action_ending: bool = False
        self.maximum_iteration_count = 10
        self._agent_map = {agent.name: agent for agent in agents}
        
    async def select_next_speaker(self, history: List) -> ChatAgent:
        """Select the next agent based on the conversation flow and context."""
        
        if self.action_ending:
            return self._agent_map.get("lego-orchestrator")
            
        if not history:
            # Start with orchestrator
            return self._agent_map.get("lego-orchestrator")
            
        last_message = history[-1] if history else None
        last_agent = getattr(last_message, 'author_name', None) if last_message else None
        
        # Define the workflow logic
        if last_agent == "lego-orchestrator":
            # After orchestrator, start with observer to analyze the field
            return self._agent_map.get("lego-observer")
            
        elif last_agent == "lego-observer" and not self.action_executing:
            # After observation, move to planner
            return self._agent_map.get("lego-planner")
            
        elif last_agent == "lego-planner":
            # After planning, execute with controller
            return self._agent_map.get("lego-controller")
            
        elif last_agent == "lego-controller":
            # After action, judge the results
            self.action_executing = True
            return self._agent_map.get("lego-observer")
            
        elif last_agent == "lego-observer" and self.action_executing:
            self.action_executing = False
            return self._agent_map.get("lego-judger")
            
        elif last_agent == "lego-judger":
            self.action_ending = True
            return self._agent_map.get("lego-orchestrator")
            
        # Default fallback
        return self._agent_map.get("lego-orchestrator")
    
    async def should_terminate(self, history: List) -> bool:
        """Check if the workflow should terminate."""
        if len(history) < 4:
            return False
            
        result = history[-4:]
        print(f"--- Agent Termination Check ---")
        for idx, h in enumerate(result):
            content = getattr(h, 'text', '') or getattr(h, 'content', '')
            print(f"{idx}: name={getattr(h, 'author_name', None)}, content={content}")
        print(f"-------------------------------")
        
        return any(
            "completed actions" in (getattr(h, 'text', '') or getattr(h, 'content', '') or '').lower() 
            for h in result
        ) or any(
            "task completed" in (getattr(h, 'text', '') or getattr(h, 'content', '') or '').lower() 
            for h in result
        )
    
        
class LegoAgent:
    """Main LEGO Agent orchestrator using Microsoft Agent Framework workflows."""

    legoOrchestratorAgent = LegoOrchestratorAgent()
    legoObserverAgent = LegoObserverAgent()
    legoPlannerAgent = LegoPlannerAgent()
    legoControllerAgent = LegoControllerAgent()
    legoJudgerAgent = LegoJudgerAgent()
    init_done = False

    async def init(self):
        if not self.init_done:
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
                        subagent="lego-controller",
                        status="robot actioned",
                        information=f,
                    )
            seen_files = current_files

    async def robot_agent_run(self, goal: str):
        await shared.mcprobot.connect()
        
        # Get agent instances
        agents = [
            self.legoOrchestratorAgent.agent,
            self.legoObserverAgent.agent,
            self.legoPlannerAgent.agent,
            self.legoControllerAgent.agent,
            self.legoJudgerAgent.agent
        ]
        
        # Build the workflow using Microsoft Agent Framework group chat pattern
        # Using custom manager for LEGO-specific agent selection logic
        shared.workflow = AgentWorkflowBuilder.create_group_chat_builder_with(
            lambda agent_list: LegoGroupChatManager(agent_list)
        ).add_participants(*agents).build()
        
        temp_folder = os.path.join('D:/gh-repo/lego-agent/lego-mcp/temp')
        monitor_task = asyncio.create_task(self.monitor_temp_folder(temp_folder))

        try:
            # Start the workflow with the user's goal
            print(f"# USER: '{goal}'")
            
            # Run the workflow
            async for event in shared.workflow.run_stream(goal):
                if isinstance(event, WorkflowEvent):
                    content = event
                    agent_name = getattr(content, 'author_name', None) or getattr(content, 'name', '*')
                    message_content = getattr(content, 'text', '') or getattr(content, 'content', '')
                    
                    print(f"\033[93m \r\n--------------------- {agent_name} start --------------------- \033[0m")
                    print(f"{message_content}")
                    print(f"\033[93m \r\n--------------------- {agent_name} end --------------------- \033[0m")

                    if shared.notify is not None:
                        if agent_name == "lego-observer" and shared.robotData.field_data is not None and "blob" in shared.robotData.field_data and shared.lastImage != shared.robotData.field_data["blob"]:
                            shared.lastImage = shared.robotData.field_data["blob"]
                            await shared.notify(
                                id="image_update",
                                subagent=agent_name,
                                status="field analysis completed",
                                content=Content(
                                    type="image",
                                    content=[
                                        {
                                            "type": "image",
                                            "description": message_content,
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
                                subagent=agent_name,
                                status="responded",
                                content=Content(
                                    type="text",
                                    content=[
                                        {
                                            "type": "text",
                                            "value": message_content,
                                        }
                                    ],
                                ),
                                output=True,
                            )

            print(f"code completed")
        finally:
            monitor_task.cancel()
            # Reset workflow state if needed
            if hasattr(shared, 'workflow') and shared.workflow:
                shared.workflow = None
        
        return "Robot agent run completed."