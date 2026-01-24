"""
LEGO Planner Agent - Creates step-by-step action plans.
"""

from typing import TYPE_CHECKING
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoPlannerAgent:
    """LEGO Planner Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-planner"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the planner agent using Microsoft Agent Framework with MCP tools.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        self._context = context
        
        # Get MCP tools from context if available
        tools = []
        if context.mcp_session is not None:
            tools = context.mcp_tools if context.mcp_tools else []
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model="gpt-4o",
                    instructions='''
You are robot planner agent. 

need to decide how the robot should action to achieve the goal. 
you must plan out each action step by step. 
you can use the robot mcp plugin to understand what actions what actions are available to the robot. 

the robot is facing east directly. treat the left bottom corner as the origin (0,0). 
the x axis is the east direction, and the y axis is the north direction. robot is facing the object directly.

when calculating the distance, you must use the following conversion: 60 pixels equal to 1 centimetre in the field data.
assuming all the objects are in a straight line, calculate distance based on x-axis ONLY. 
when robot needs to move multiple time, remember to calculate and exclude the distance that it has moved.

each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.

below is the example format to output the plan with multiple steps. 
MUST MUST only response the steps in the same array as the json output.
Never try to run mcp action directly, just plan the steps and return the json array.

[   
    {
        "action": "robotmcp-robot_move",
        "args": {
            "robot_id": "1",
            "distance": 200
        },
        "explain": "move the robot 200mm forward in the current direction, which is east."
    },
    {
        ....
    },
    {
        ....
    }
]  
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
            description="Creates step-by-step action plans for the robot",
            tools=tools
        )

    async def exec(self, message: str) -> str:
        """Execute the planner agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
