from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared
from ..context import AgentContext
from . import YELLOW, RESET


class ControllerChatAgent(ChatAgent):
    """ChatAgent subclass that always returns structured FieldData."""

    async def run(self, messages=None, **kwargs):
        response = await super().run(messages, **kwargs)
        print(f"{YELLOW}# lego-controller:{RESET}\r\n{response}\r\n")
        return response
    
    
class LegoControllerAgent:
    AGENT_NAME = "lego-controller"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        self._context = context
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model="gpt-4.1",
                    instructions='''
You are robot controller agent. need to follow the plan to control the robot to action. 
do one step at a time and wait for earlier action to complete. 
MUST run all the steps using robot function and action physically without skipping any step.
dont ask for any confirmation, just follow the plan step by step.

You do not know if the robot action is successful or not, and you should not only say the action has been done.
NEVER say 'task is completed' or 'successfully completed the task', just say the action is done.
NEVER repeat other agent's response, just provide your own answer.
After performing all actions, say that 'detection_result' is no longer valid, need to ask observer agent to provide the latest field data.'''
                ),
            )
        
        self.agent = ControllerChatAgent(
            chat_client=AzureAIAgentClient(
                    project_endpoint=shared.AZURE_AI_PROJECT_ENDPOINT,
                    model_deployment_name=shared.AZURE_OPENAI_DEPLOYMENT,
                    agent_name=agentdef.name,
                    credential=shared.credential,
                ),
            name=self.AGENT_NAME,
            description="Executes physical robot actions via MCP tools",
            tools=context.mcp_legorobot_action
        )
