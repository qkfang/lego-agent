"""
LegoAgent - Main LEGO Agent orchestrator using Microsoft Agent Framework workflows.
"""

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
    """
    Main LEGO Agent orchestrator using Microsoft Agent Framework workflows.
    
    This class coordinates multiple specialized agents to control a LEGO robot:
    - Orchestrator: Coordinates the overall workflow
    - Observer: Captures and analyzes the robot field state
    - Planner: Creates step-by-step action plans
    - Controller: Executes physical robot actions
    - Judge: Evaluates goal completion
    
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
        self._max_iterations = 10
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
        """Get the agent context."""
        return self._context

    async def init(self):
        """Initialize all sub-agents."""
        if not self._init_done:
            await self._orchestrator.init(self._context)
            await self._observer.init(self._context)
            await self._planner.init(self._context)
            await self._controller.init(self._context)
            await self._judge.init(self._context)
            self._init_done = True

    def _build_workflow(self):
        """
        Build and return the workflow.
        
        Returns:
            The built workflow (not wrapped as agent)
        """
        orchestrator_executor = AgentExecutor(self._orchestrator.agent, id="lego-orchestrator")
        observer_executor = AgentExecutor(self._observer.agent, id="lego-observer")
        planner_executor = AgentExecutor(self._planner.agent, id="lego-planner")
        controller_executor = AgentExecutor(self._controller.agent, id="lego-controller")
        judge_executor = AgentExecutor(self._judge.agent, id="lego-judge")
        
        workflow = (
            WorkflowBuilder()
            .set_start_executor(orchestrator_executor)
            .add_edge(orchestrator_executor, observer_executor)
            .add_edge(observer_executor, planner_executor)
            .add_edge(planner_executor, controller_executor)
            .add_edge(controller_executor, observer_executor)
            .add_edge(observer_executor, judge_executor)
            .add_edge(
                judge_executor, 
                observer_executor,
                condition=lambda result: not result.completed and self._check_iteration_limit()
            )
            .build()
        )
        return workflow

    async def as_workflow_agent(self):
        """
        Create and return the workflow wrapped as an agent for HTTP serving.
        
        This is useful for DevUI and HTTP server integration.
        
        Returns:
            The workflow wrapped as an agent
        """
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
        """
        Run the agent workflow with the given goal.
        
        Args:
            goal: The goal to achieve (e.g., "Pick up the coke and deliver it to Bowser")
            
        Returns:
            A completion message
        """
        # Reset iteration counter
        self._iteration_count = 0
        
        # Build the workflow
        self._context.workflow = self._build_workflow()
        
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
                        executor_id = getattr(complete, 'executor_id', 'unknown')
                        data = getattr(complete, 'data', None)
                        
                        # Print the executor completion
                        print(f"\033[92m[{executor_id} completed]\033[0m")
                        
                        # Store judgement result if this is the decision executor
                        if executor_id == 'judge_decision_executor' and isinstance(data, JudgementResult):
                            self._last_judgement = data
                        
                        # Extract and print response
                        if data is not None:
                            # Handle list of responses (AgentExecutor returns a list)
                            if isinstance(data, list) and len(data) > 0:
                                response = data[0]
                                if hasattr(response, 'agent_run_response'):
                                    # It's an AgentExecutorResponse
                                    agent_response = response.agent_run_response
                                    if hasattr(agent_response, 'content'):
                                        content = agent_response.content
                                        print(f"  → {content}")
                                    elif hasattr(response, 'full_conversation') and response.full_conversation:
                                        # Get last message from conversation
                                        last_msg = response.full_conversation[-1]
                                        content = getattr(last_msg, 'content', '') or getattr(last_msg, 'text', '')
                                        if content:
                                            print(f"  → {content}")
                            else:
                                # Generic data - debug output
                                print(f"  → Type: {type(data).__name__}, Value: {str(data)[:300]}")
                    case WorkflowOutputEvent() as output:
                        result = output.data
                        if isinstance(result, JudgementResult):
                            status = "✅ COMPLETED" if result.completed else "❌ MAX ITERATIONS"
                            print(f"\033[93m{status}\033[0m: {result.reason}")
                        else:
                            print(f"\033[93mWorkflow output:\033[0m {result}")
                        return "Robot agent run completed."

            print(f"\n\033[96m{'='*60}\033[0m")
            print(f"\033[96mWorkflow completed\033[0m")
            if self._last_judgement:
                status_icon = "✅" if self._last_judgement.completed else "❌"
                print(f"{status_icon} Final Decision: completed={self._last_judgement.completed}")
                if self._last_judgement.reason:
                    reason_preview = self._last_judgement.reason[:150] + "..." if len(self._last_judgement.reason) > 150 else self._last_judgement.reason
                    print(f"Reason: {reason_preview}")
            print(f"\033[96m{'='*60}\033[0m")
        finally:
            monitor_task.cancel()
            if self._context.workflow:
                self._context.workflow = None
        
        return "Robot agent run completed."
    
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
