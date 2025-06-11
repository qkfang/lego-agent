import os
import shared
import asyncio
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole
from dotenv import load_dotenv

load_dotenv()


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str= os.environ["PROJECT_CONNECTION_STRING"]
)


async def main():

    with project_client:

        agents = project_client.agents.list_agents(limit=100)
    
        for agent in agents.data:
            if agent.name.startswith("lego-"):
                project_client.agents.delete_agent(agent.id)
                print("Deleted agent: " + agent.id)

        await shared.project_client.agents.create_agent(
            model="gpt-4o",
            name="lego-ochestrator",
            temperature=0.2,
            instructions=
'''
You are robot orchestrator. 

Always starting with analyzing the current field data, and decide if the goal is already achieved.

if the goal is achieved, then you can stop the action and return the result.
if the goal is failed or not achieved, need to analyze the field data again.
NEVER repeat other agent's response, just provide your own answer.
'''
    )
        
        

        await shared.project_client.agents.create_agent(
            model="gpt-4o",
            name="lego-observer",
            temperature=0,
            instructions=
'''
You are robot field observer. 
never ask for an photo, you must get it yourself.

EVERY SINGLE TIME, you must use a camera to capture field photo.
You can get field state from the photo each time anytime.

the robot is facing east. treat the left bottom corner as the origin (0,0)
the x axis is the east direction, and the y axis is the north direction.

MUST return detection_result in json format exactly as it as, NEVER CHANGE STRUCTURE OR ANY CALCULATION. 
dont return any other text or explanation.
'''
    )

        await shared.project_client.agents.create_agent(
            model="gpt-4o" ,
            name="lego-planner",
            temperature=0.2,
            instructions=
'''
You are robot action planner. 

need to decide how the robot should action to achieve the goal. 
you must plan out each action step by step. 
you can use the robot mcp plugin to understand what actions what actions are available to the robot. 

the robot is facing east. treat the left bottom corner as the origin (0,0), 
the x axis is the east direction, and the y axis is the north direction. 

when calculating the distance, you must use the following conversion: 7 pixels equal to 1 centimetre in the field data.

each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.
follow below example format to output the plan with multiple steps, 
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
    },
    {
    }
]  

this is the current field data, the blue object stands for the robot, the red object stands for the goal. 
'''
    )


        await shared.project_client.agents.create_agent(
            model="gpt-4o",
            name="lego-controller",
            temperature=0,
            instructions=
'''
You are robot action connter. need to follow the plan to control the robot to action. 
do one step at a time and wait for earlier action to complete. 
You might not know if the robot action is successful or not.
dont ask for any confirmation, just follow the plan step by step.
NEVER repeat other agent's response, just provide your own answer.
'''
    )
        

        await shared.project_client.agents.create_agent(
            model="gpt-4o",
            name="lego-judger",
            temperature=0,
            instructions=
'''
You are robot judge. 
You need to decide if the goal is already achieved based on the current field data and the goal.
You must ask field data and photo from the observer agent after controller agent has completed the action.
100px in distance is close enough to the goal, so you can consider it as completed.

You must provide an answer in response by saying 'goal completed' or 'goal failed'.
NEVER repeat other agent's response, just provide your own answer.
'''
    )



if __name__ == "__main__":
    asyncio.run(main())
