"""
LEGO Planner Agent - Creates step-by-step action plans.
"""

from typing import TYPE_CHECKING
from pathlib import Path
from agent_framework.declarative import AgentFactory
from .. import shared

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoPlannerAgent:
    """LEGO Planner Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-planner"
    
    def __init__(self):
        self.agent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the planner agent using declarative YAML with MCP tools.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        self._context = context
        
        # Get the path to the YAML file
        prompts_dir = Path(__file__).parent.parent / "prompts"
        yaml_path = prompts_dir / "planner.yaml"
        
        # Create agent from declarative YAML using AgentFactory
        # MCP tools should be configured in the YAML or passed through context
        agent_factory = AgentFactory(
            client_kwargs={"credential": shared.credential}
        )
        self.agent = agent_factory.create_agent_from_yaml_path(yaml_path)

    async def exec(self, message: str) -> str:
        """Execute the planner agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
