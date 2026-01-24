import os
import lego_robot_agent.shared as shared
import asyncio
from azure.identity import DefaultAzureCredential, AzureCliCredential
from agent_framework.azure import AzureOpenAIResponsesClient
from dotenv import load_dotenv

load_dotenv()

# Microsoft Agent Framework - Azure OpenAI Responses Client
azure_client = AzureOpenAIResponsesClient(
    endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
    deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    credential=AzureCliCredential(),
)


async def main():
    """
    Main function to demonstrate agent creation with Microsoft Agent Framework.
    
    Note: In the new framework, agents are created on-demand and don't need
    to be pre-registered in a service. The cleanup and creation pattern
    from Azure AI Foundry is no longer needed.
    """
    
    # Create orchestrator agent
    orchestrator = azure_client.create_agent(
        name="lego-orchestrator",
        instructions='''
You are robot orchestrator. 

Always starting with analyzing the current field data, and decide if the goal is already achieved.

if the goal is achieved, then you can stop the action and return the result.
if the goal is failed or not achieved, need to analyze the field data again.
NEVER repeat other agent's response, just provide your own answer.
'''
    )
    print(f"Created agent: lego-orchestrator")
    
    # Create observer agent
    observer = azure_client.create_agent(
        name="lego-observer",
        instructions='''
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
    print(f"Created agent: lego-observer")
    
    # Create planner agent
    planner = azure_client.create_agent(
        name="lego-planner",
        instructions='''
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
    }
]  
'''
    )
    print(f"Created agent: lego-planner")
    
    # Create controller agent
    controller = azure_client.create_agent(
        name="lego-controller",
        instructions='''
You are robot action controller. need to follow the plan to control the robot to action. 
do one step at a time and wait for earlier action to complete. 
You might not know if the robot action is successful or not.
dont ask for any confirmation, just follow the plan step by step.
NEVER repeat other agent's response, just provide your own answer.
'''
    )
    print(f"Created agent: lego-controller")
    
    # Create judger agent
    judger = azure_client.create_agent(
        name="lego-judger",
        instructions='''
You are robot judge. 
You need to decide if the goal is already achieved based on the current field data and the goal.
You must ask field data and photo from the observer agent after controller agent has completed the action.
100px in distance is close enough to the goal, so you can consider it as completed.

You must provide an answer in response by saying 'goal completed' or 'goal failed'.
NEVER repeat other agent's response, just provide your own answer.
'''
    )
    print(f"Created agent: lego-judger")
    
    print("\nAll agents created successfully with Microsoft Agent Framework!")
    print("Note: Agents are now created on-demand and don't persist in a service.")


if __name__ == "__main__":
    asyncio.run(main())
