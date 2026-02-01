"""
LEGO Orchestrator Agent - Coordinates the multi-agent workflow.
"""

from typing import TYPE_CHECKING
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared
from ..util.yaml_loader import get_agent_instructions, get_agent_model

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoOrchestratorAgent:
    """LEGO Orchestrator Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-orchestrator"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the orchestrator agent using Microsoft Agent Framework.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        self._context = context
        
        # Load instructions from YAML file
        instructions = get_agent_instructions('orchestrator')
        model_id = get_agent_model('orchestrator')
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model=model_id,
                    instructions=instructions
                ),
            )
        
        self.agent = ChatAgent(
            chat_client=AzureAIAgentClient(
                    project_endpoint=shared.AZURE_AI_PROJECT_ENDPOINT,
                    model_deployment_name=shared.AZURE_OPENAI_DEPLOYMENT,
                    agent_name=agentdef.name,
                    credential=shared.credential,
                ),
            name=self.AGENT_NAME,
            description="Coordinates the overall workflow and decides when the task is complete"
        )

    async def exec(self, message: str) -> str:
        """Execute the orchestrator agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
