"""
Agent Event Handler Module

This module has been migrated from Azure AI Foundry to Microsoft Agent Framework.
The old handler pattern is no longer needed as the Agent Framework handles 
tool execution and event streaming through workflows.

The classes below are kept for backward compatibility but are not actively used
in the new workflow-based architecture.
"""

import inspect
import json
from typing import Any, Union, Callable, Dict
from prompty.tracer import trace

from model import AgentUpdateEvent, Content, Function


class AgentEventHandler:
    """
    Simplified event handler for Microsoft Agent Framework.
    
    In the new framework, events are handled through workflow streaming
    rather than a dedicated event handler class.
    """

    def __init__(
        self,
        tools: Dict[str, Function],
        notify: AgentUpdateEvent,
    ) -> None:
        self.notify = notify
        self.tools = tools
        self.history: list[Dict[str, Any]] = []

    @trace(name="send_agent_status")
    async def add_message(
        self,
        message_id: str,
        status: str,
        content: Any = None,
        output: bool = False,
    ) -> None:
        """Add a message to the event history and notify."""
        
        await self.notify(
            id=message_id,
            status=status,
            content=content,
            output=output,
        )
        
        self.history.append({
            "id": message_id,
            "status": status,
            "content": content,
        })

    async def on_error(self, data: str) -> None:
        """Handle error events."""
        print(f"An error occurred. Data: {data}")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        """Handle unhandled events."""
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    async def execute_tool_call(
        self, 
        function_name: str, 
        arguments: Dict[str, Any]
    ) -> Any:
        """Execute a tool call by function name with given arguments."""
        
        if function_name not in self.tools:
            raise ValueError(f"Function {function_name} not found in tools.")

        function = self.tools[function_name]
        if not inspect.iscoroutinefunction(function.func):
            raise ValueError(f"Function {function_name} is not a coroutine function.")

        arguments["notify"] = self.notify
        print(f"Executing tool call: {function_name}")
        return await function.func(**arguments)


# Deprecated: SustineoAgentEventHandler
# This class was used with Azure AI Foundry's AsyncAgentEventHandler.
# It is kept here only for reference during migration.
# The new Microsoft Agent Framework uses workflow-based event handling.
SustineoAgentEventHandler = AgentEventHandler
