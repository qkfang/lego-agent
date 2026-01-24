import json
import shared
import re
from agent_framework import ChatAgent


class LegoPlannerAgent:
    """LEGO Planner Agent using Microsoft Agent Framework."""
    agent: ChatAgent = None
    agentName = "lego-planner"

    def __init__(self):
        self.agent = None

    async def init(self):
        """Initialize the planner agent using Microsoft Agent Framework with MCP tools."""
        
        # Get MCP tools from shared if available
        tools = []
        if shared.mcprobot is not None:
            tools = shared.robotmcptools if shared.robotmcptools else []
        
        # Create agent with MCP robot tools
        self.agent = ChatAgent(
            chat_client=shared.azure_client,
            name=self.agentName,
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

''',
            tools=tools,
            description="Robot action planner that creates step-by-step action plans"
        )

    async def exec(self, message: str):
        """Execute the planner agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.agentName}: {response}")
        return str(response)
