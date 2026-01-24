"""
LEGO Judger Agent - Evaluates goal completion.
"""

from typing import TYPE_CHECKING
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoJudgerAgent:
    """LEGO Judger Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-judger"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the judger agent using Microsoft Agent Framework.
        
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
You are robot judger agent. 

You need to decide if the goal is already achieved based on the current field data and the goal.
when the distance between coke and bowser is less than 180 pixels, it means that the robot has delievered the coke to the bowser successfully.
robot position should not be considered.

You must provide an answer in response by saying **goal completed** or **goal failed**. Also include the reason for your decision.
NEVER repeat other agent's response, just provide your own answer.
'''
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
            description="Evaluates goal completion based on field data"
        )

    async def exec(self, message: str) -> str:
        """Execute the judger agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
