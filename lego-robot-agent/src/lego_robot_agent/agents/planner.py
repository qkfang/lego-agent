from typing import TYPE_CHECKING, Any
from pydantic import BaseModel
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared
from ..context import AgentContext
from ..type.models import RobotPlan


class PlannerChatAgent(ChatAgent):
    """ChatAgent subclass that always returns structured RobotPlan."""

    async def run(self, messages=None, **kwargs):
        kwargs.setdefault("response_format", RobotPlan)
        response = await super().run(messages, **kwargs)
        print(f"# lego-planner: {response}")
        return response


class LegoPlannerAgent:
    AGENT_NAME = "lego-planner"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        self._context = context
        
        # Get MCP tools from context if available
        tools = []
        if context.mcp_legorobot_action is not None:
            tools = context.mcp_legorobot_action if context.mcp_legorobot_action else []
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model="gpt-4.1",
                    instructions='''
You are robot planner agent. 

need to decide how the robot should action to achieve the goal. 
you must plan out each action step by step. 
you can use the robot mcp plugin to understand what actions what actions are available to the robot. 

the robot is facing east directly. treat the left bottom corner as the origin (0,0). 
the x axis is the east direction, and the y axis is the north direction. robot is facing the object directly.

when calculating the distance, you must use the following conversion: 300 pixels equal to 1 centimetre in the field data.
assuming all the objects are in a straight line, calculate distance based on x-axis ONLY. Don't need to turn or rotate degrees.
when robot needs to move multiple time, remember to calculate and exclude the distance that it has moved.

each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.

below is the example format to output the plan with multiple steps. 
MUST return ONLY valid JSON in this exact structure, no other text or explanation.
Never try to run mcp action directly, just plan the steps and return the json object.

{
  "steps": [   
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
}
'''
                ),
            )
        
        self.agent = PlannerChatAgent(
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
