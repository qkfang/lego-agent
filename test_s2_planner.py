import json
import test_shared
import re
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent, AzureAIAgentSettings
from test_shared import robotData


async def run_step2():

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o" ,
        name="lego-api333",
        instructions=
'''
You are robot action planner. need to decide how the robot should action to achieve the goal. you must plan out each action step by step. you can use the robot mcp plugin to understand what actions what actions are available to the robot. 

the robot is facing east. treat the left bottom corner as the origin (0,0), the x axis is the east direction, and the y axis is the north direction. 
follow below example format to output the plan with multiple steps, each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.
[   
    {
        "action": "AIFoundryAgents-robot_move",
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
''' + robotData.step1_analyze_json_data()
    )

    agent = AzureAIAgent(
        client=test_shared.project_client,
        definition=agentdef,
        plugins=[test_shared.mcp],
    )

    response = await agent.get_response(
        messages=
'''
Now make a plan to move robot to the red object and pick it up. output the plan in json format, each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.
''',
        thread=test_shared.thread,
    )
    print(f"# {response.name}: {response}")

    match = re.search(r'(\[\s*{.*?}\s*\])', str(response), re.DOTALL)
    if match:
        plan_json = match.group(1)
        plan = json.loads(plan_json)    
        
        with open(robotData.step2_plan_json(), "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)


