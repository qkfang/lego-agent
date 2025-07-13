import json
import shared
import re
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent, AzureAIAgentSettings


class LegoPlannerAgent:
    agent = None
    agentName = "lego-planner"

    def __init__(self):
        self.agent = None

    async def init(self):

        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.agentName), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_agent(
                model="gpt-4o" ,
                name=self.agentName,
                temperature=0.2,
                instructions=
'''
You are robot planner agent. 

need to decide how the robot should action to achieve the goal. 
you must plan out each action step by step. 
you can use the robot mcp plugin to understand what actions what actions are available to the robot. 

the robot is facing east directly. treat the left bottom corner as the origin (0,0). 
the x axis is the east direction, and the y axis is the north direction. robot is facing the object directly.

when calculating the distance, you must use the following conversion: 10 pixels equal to 1 centimetre in the field data.

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
        )

        self.agent = AzureAIAgent(
            client=shared.project_client,
            definition=agentdef,
            plugins=[shared.mcprobot],
        )


    async def exec(self, message: str):
        response = await self.agent.get_response(
                                        messages= message, 
                                        thread=shared.thread
                                    )
        print(f"# {response.name}: {response.message}")
        return str(response)
