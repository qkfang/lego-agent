"""
LegoAgent - Main LEGO Agent orchestrator using Microsoft Agent Framework workflows.
"""

import json
import os
import asyncio
from typing import List, Callable, Coroutine, Any, Optional

from agent_framework import GroupChatBuilder, GroupChatState, WorkflowEvent, ChatMessage
from agent_framework import AgentRunEvent, Role, WorkflowOutputEvent, ExecutorCompletedEvent

from .context import AgentContext
from .models import Content
from .agents import (
    LegoOrchestratorAgent,
    LegoObserverAgent,
    LegoPlannerAgent,
    LegoControllerAgent,
    LegoJudgerAgent,
)


class LegoAgent:
    """
    Main LEGO Agent orchestrator using Microsoft Agent Framework workflows.
    
    This class coordinates multiple specialized agents to control a LEGO robot:
    - Orchestrator: Coordinates the overall workflow
    - Observer: Captures and analyzes the robot field state
    - Planner: Creates step-by-step action plans
    - Controller: Executes physical robot actions
    - Judger: Evaluates goal completion
    
    Usage:
        context = AgentContext(azure_client=..., mcp_session=...)
        agent = LegoAgent(context)
        await agent.init()
        await agent.run("Pick up the coke and deliver it to Bowser")
    """
    
    def __init__(self, context: AgentContext):
        """
        Initialize the LegoAgent with a context.
        
        Args:
            context: The agent context containing all dependencies
        """
        self._context = context
        self._init_done = False
        
        # Workflow state
        self._action_executing = False
        self._action_ending = False
        self._agent_map = {}
        
        # Sub-agents
        self._orchestrator = LegoOrchestratorAgent()
        self._observer = LegoObserverAgent()
        self._planner = LegoPlannerAgent()
        self._controller = LegoControllerAgent()
        self._judger = LegoJudgerAgent()

    @property
    def context(self) -> AgentContext:
        """Get the agent context."""
        return self._context

    async def init(self):
        """Initialize all sub-agents."""
        if not self._init_done:
            await self._orchestrator.init(self._context)
            await self._observer.init(self._context)
            await self._planner.init(self._context)
            await self._controller.init(self._context)
            await self._judger.init(self._context)
            self._init_done = True

    async def _select_next_speaker(self, state: GroupChatState) -> str:
        """Select the next agent based on the conversation flow and context."""
        history = state.conversation
        
        if self._action_ending:
            return "lego-orchestrator"
            
        if not history:
            return "lego-orchestrator"
            
        last_message = history[-1] if history else None
        last_agent = getattr(last_message, 'author_name', None) if last_message else None
        
        if last_agent == "lego-orchestrator":
            return "lego-observer"
            
        elif last_agent == "lego-observer" and not self._action_executing:
            return "lego-planner"
            
        elif last_agent == "lego-planner":
            return "lego-controller"
            
        elif last_agent == "lego-controller":
            self._action_executing = True
            return "lego-observer"
            
        elif last_agent == "lego-observer" and self._action_executing:
            self._action_executing = False
            return "lego-judger"
            
        elif last_agent == "lego-judger":
            self._action_ending = True
            return "lego-orchestrator"
            
        return "lego-orchestrator"

    def _termination_condition(self, conversation: List[ChatMessage]) -> bool:
        """Check if the workflow should terminate."""
        if len(conversation) < 4:
            return False
            
        result = conversation[-4:]
        print(f"--- Agent Termination Check ---")
        # for idx, h in enumerate(result):
        #     content = getattr(h, 'text', '') or getattr(h, 'content', '')
        #     print(f"{idx}: name={getattr(h, 'author_name', None)}, content={content}")
        print(f"-------------------------------")
        
        return any(
            "completed actions" in (getattr(h, 'text', '') or getattr(h, 'content', '') or '').lower() 
            for h in result
        ) or any(
            "task completed" in (getattr(h, 'text', '') or getattr(h, 'content', '') or '').lower() 
            for h in result
        )

    async def _monitor_temp_folder(self, poll_interval: float = 2.0):
        """Monitor the temp folder for new files and send notifications."""
        temp_folder = self._context.temp_folder
        seen_files = set(os.listdir(temp_folder)) if os.path.exists(temp_folder) else set()
        
        while True:
            await asyncio.sleep(poll_interval)
            if not os.path.exists(temp_folder):
                continue
            current_files = set(os.listdir(temp_folder))
            new_files = current_files - seen_files
            if new_files:
                for f in new_files:
                    await self._context.notify(
                        id="lego-controller",
                        subagent="lego-controller",
                        status="robot actioned",
                        information=f,
                    )
            seen_files = current_files

    async def run(self, goal: str) -> str:
        """
        Run the agent workflow with the given goal.
        
        Args:
            goal: The goal to achieve (e.g., "Pick up the coke and deliver it to Bowser")
            
        Returns:
            A completion message
        """
        # Reset state for new run
        self._action_executing = False
        self._action_ending = False
        
        # Connect MCP if available
        # if self._context.mcp_session is not None:
        #     await self._context.mcp_session.connect()
        
        # Get agent instances
        agents = [
            self._orchestrator.agent,
            self._observer.agent,
            self._planner.agent,
            self._controller.agent,
            self._judger.agent
        ]
        
        # Build agent map
        self._agent_map = {agent.name: agent for agent in agents}
        
        # Build the workflow
        self._context.workflow = (
            GroupChatBuilder()
            .with_select_speaker_func(self._select_next_speaker)
            .with_termination_condition(self._termination_condition)
            .with_max_rounds(10)
            .participants(agents)
            .build()
        )
        
        monitor_task = asyncio.create_task(self._monitor_temp_folder())

        try:
            print(f"# USER: '{goal}'")
            
            async for event in self._context.workflow.run_stream(goal):
                match event:
                    case AgentRunEvent() as agent_event:
                        agent_name = getattr(agent_event, 'agent_name', 'unknown')
                        message = getattr(agent_event, 'message', None)
                        if message:
                            content = getattr(message, 'content', '') or getattr(message, 'text', '')
                            print(f"\033[94m[{agent_name}]\033[0m: {content}")
                    case ExecutorCompletedEvent() as complete:
                        agent_name = getattr(complete, 'executor_id', 'unknown')
                        data = getattr(complete, 'data', None)
                        if data:
                            content = getattr(data[0], 'agent_response', '')
                            print(f"\033[92m[{agent_name} completed]\033[0m: {content}")
                    case WorkflowOutputEvent() as output:
                        print(f"\033[93mWorkflow produced output:\033[0m {output.data}")
                        return

            print(f"code completed")
        finally:
            monitor_task.cancel()
            if self._context.workflow:
                self._context.workflow = None
        
        return "Robot agent run completed."

    async def _handle_workflow_event(self, event: ExecutorCompletedEvent):
        """Handle a workflow event and send notifications."""
        print(f"==={event.data}")
        content = event
        agent_name = getattr(content, 'author_name', None) or getattr(content, 'name', '*')
        message_content = getattr(content, 'message', '') or getattr(content, 'content', '')
        
        print(f"\033[93m \r\n--------------------- {agent_name} start --------------------- \033[0m")
        print(f"{content}")
        print(f"{message_content}")
        print(f"\033[93m \r\n--------------------- {agent_name} end --------------------- \033[0m")

        if self._context.notify_callback is not None:
            robot_data = self._context.robot_data
            
            if (agent_name == "lego-observer" 
                and robot_data.field_data is not None 
                and "blob" in robot_data.field_data 
                and self._context.last_image != robot_data.field_data["blob"]):
                
                self._context.last_image = robot_data.field_data["blob"]
                await self._context.notify(
                    id="image_update",
                    subagent=agent_name,
                    status="field analysis completed",
                    content=Content(
                        type="image",
                        content=[
                            {
                                "type": "image",
                                "description": message_content,
                                "image_url": robot_data.field_data["blob"],
                                "kind": 'image',
                            }
                        ],
                    ),
                    output=True,
                )
            else:
                await self._context.notify(
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
