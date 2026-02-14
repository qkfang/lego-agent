import json
import os
import asyncio
from typing import List, Callable, Coroutine, Any, Optional
from dataclasses import dataclass

from agent_framework import WorkflowBuilder, WorkflowContext, WorkflowEvent, ChatMessage
from agent_framework import AgentRunEvent, Role, WorkflowOutputEvent, ExecutorCompletedEvent
from agent_framework import AgentExecutor, AgentExecutorRequest, AgentExecutorResponse, executor

from .context import AgentContext
from .models import Content
from .agents import (
    LegoOrchestratorAgent,
    LegoObserverAgent,
    LegoPlannerAgent,
    LegoControllerAgent,
    LegoJudgeAgent,
)


class LegoAgent:

    def __init__(self, context: AgentContext):
        self._context = context
        self._init_done = False
        
        # Workflow state
        self._max_iterations = 2
        self._iteration_count = 0
        self._last_judgement = None
        
        # Sub-agents
        self._orchestrator = LegoOrchestratorAgent()
        self._observer = LegoObserverAgent()
        self._planner = LegoPlannerAgent()
        self._controller = LegoControllerAgent()
        self._judge = LegoJudgeAgent()

    @property
    def context(self) -> AgentContext:
        return self._context

    async def init(self):
        if not self._init_done:
            await self._orchestrator.init(self._context)
            await self._observer.init(self._context)
            await self._planner.init(self._context)
            await self._controller.init(self._context)
            await self._judge.init(self._context)
            self._init_done = True

    def _build_workflow(self):
        orchestrator_executor = AgentExecutor(self._orchestrator.agent, id="lego-orchestrator")
        observer_executor = AgentExecutor(self._observer.agent, id="lego-observer")
        planner_executor = AgentExecutor(self._planner.agent, id="lego-planner")
        controller_executor = AgentExecutor(self._controller.agent, id="lego-controller")
        observer_post_executor = AgentExecutor(self._observer.agent, id="lego-observer-post")
        judge_executor = AgentExecutor(self._judge.agent, id="lego-judge")
        
        workflow = (
            WorkflowBuilder()
            .set_start_executor(orchestrator_executor)
            .add_edge(orchestrator_executor, observer_executor)
            .add_edge(observer_executor, planner_executor)
            .add_edge(planner_executor, controller_executor)
            .add_edge(controller_executor, observer_post_executor)
            .add_edge(observer_post_executor, judge_executor)
            .add_edge(
                judge_executor, 
                observer_executor,
                condition=lambda result: not self._is_goal_completed(result.agent_run_response.text) and self._check_iteration_limit()
            )
            .build()
        )
        return workflow

    async def as_workflow_agent(self):
        await self.init()
        self._iteration_count = 0
        return self._build_workflow().as_agent()

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
        self._iteration_count = 0
        self._context.workflow = self._build_workflow()
        
        monitor_task = asyncio.create_task(self._monitor_temp_folder())

        try:
            print(f"# USER: '{goal}'")
            
            result = await self._context.workflow.run(goal)
            
            print(f"\n\033[96m{'='*60}\033[0m")
            print(f"\033[96mWorkflow completed\033[0m")
            print(f"Result: {result}")
            print(f"\033[96m{'='*60}\033[0m")
        finally:
            monitor_task.cancel()
            if self._context.workflow:
                self._context.workflow = None
        
        return "Robot agent run completed."
    
    def _is_goal_completed(self, text: str) -> bool:
        try:
            data = json.loads(text)
            return data.get("completed") is True
        except (json.JSONDecodeError, AttributeError):
            return False

    def _check_iteration_limit(self) -> bool:
        """Check if we're under iteration limit and increment counter."""
        self._iteration_count += 1
        under_limit = self._iteration_count < self._max_iterations
        if not under_limit:
            print(f"⚠️  Max iterations ({self._max_iterations}) reached")
        return under_limit

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
