"""
LEGO Controller Agent - Executes physical robot actions via MCP tools.
"""

from typing import TYPE_CHECKING
from pathlib import Path
from agent_framework.declarative import AgentFactory
from .. import shared

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoControllerAgent:
    """LEGO Controller Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-controller"
    
    def __init__(self):
        self.agent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the controller agent using declarative YAML with MCP tools.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        self._context = context
        
        # Get MCP tools from context if available
        tools = []
        if context.mcp_session is not None:
            tools = context.mcp_tools if context.mcp_tools else []

        # Get the path to the YAML file
        agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
        yaml_path = agents_dir / "controller.yaml"
        
        # Create agent from declarative YAML using AgentFactory with MCP tools
        agent_factory = AgentFactory(
            client_kwargs={"credential": shared.credential}
        )
        self.agent = agent_factory.create_agent_from_yaml_path(yaml_path)
        
        # If we have MCP tools, add them to the agent
        if tools:
            # The declarative agent should already have tools configured
            # but we can pass them via the agent's tools attribute if needed
            pass

    async def exec(self, message: str) -> str:
        """Execute the controller agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
