"""
LEGO Orchestrator Agent - Coordinates the multi-agent workflow.
"""

from typing import TYPE_CHECKING
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared

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
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model="gpt-4o",
                    instructions='''
You are robot orchestrator agent. 
Always starting with analyzing the current field data.
When judger agent has already determined that the goal is completed or failed, you must end the conversation by saying 'agents have completed actions' and provide a summary of past activities.
It's always good to ask user to check the final result in the end.
'''
                ),
            )
        
        self.agent = ChatAgent(
            chat_client=AzureAIAgentClient(
                    project_endpoint=shared.AZURE_AI_PROJECT_ENDPOINT,
                    model_deployment_name=shared.AZURE_OPENAI_DEPLOYMENT,
                    agent_name=agentdef.name,
                    credential=shared.credential,
                )
        )

    async def exec(self, message: str) -> str:
        """Execute the orchestrator agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
