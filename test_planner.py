import json
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent, AzureAIAgentSettings
import test_shared
from test_shared import robotData


async def run_step2():

    with open(robotData.step1_analyze_json, "r", encoding="utf-8") as file:
        contents = file.read()

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o" ,
        name="lego-api333",
        instructions=
'''
You are robot action planner. need to decide how the robot should action to achieve the goal. you must plan out each action step by step. you can use the robot mcp plugin to understand what actions what actions are available to the robot. 

the robot is facing east. treat the left bottom corner as the origin (0,0), the x axis is the east direction, and the y axis is the north direction. 
follow below format to output the plan, each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.
[   
{
"action": "AIFoundryAgents-robot_move",
"args": {
    "robot_id": "1",
    "distance": 200
},
"explain": "move the robot 200mm forward in the current direction, which is east."
}  
]  

this is the current field data, the blue object stands for the robot, the red object stands for the goal. 
''' + contents
    )
    # [END create_agent_with_azure_ai_search_tool]
    # print(f"Created agent, ID: {agentdef.id}")

    agent = AzureAIAgent(
        client=test_shared.project_client,
        definition=agentdef,
        plugins=[test_shared.mcp],  # Add the plugin to the agent
        
    )

    # Create thread for communication
    thread = None

    async for response in agent.invoke(
                        messages=
'''
Now make a plan to move robot to the red object and pick it up. output the plan in json format, each step should be a json object with "action" and "args" fields. The action is the robot action name, and args is the arguments for the action.
''',
                        thread=thread,
                    ):
        print(f"# {response.name}: {response}")
        thread = response.thread

        # Extract JSON block from response
        import re

        match = re.search(r'(\[\s*{.*?}\s*\])', str(response), re.DOTALL)
        if match:
            plan_json = match.group(1)
            try:
                plan = json.loads(plan_json)    
                
                robotData.step2_plan_json = f"{robotData.root}/{robotData.runid}_step2_plan_json.json"
                with open(robotData.step2_plan_json, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2)

                print("Plan saved to step2-plan-data.json")
            except Exception as e:
                print(f"Failed to parse or save plan: {e}")

