import json
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent, AzureAIAgentSettings

from api.agent.agents import processImage
from test_shared import robotData
import test_shared


async def run_step1():
    robotData.step1_analyze_img = f"{robotData.root}/{robotData.runid}_step1_analyze_img.jpg"
    robotData.step1_analyze_json = f"{robotData.root}/{robotData.runid}_step1_analyze_json.json"

    data = await processImage(robotData.step0_img_path, robotData.step1_analyze_img, robotData.step1_analyze_json)
    print(json.dumps(data, indent=2))

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o" , #""os.environ["MODEL_DEPLOYMENT_NAME"],
        name="lego-api333",
        instructions="You are robot action planner. need to decide how the robot should action to achieve the goal. you must plan out each action step by step. you can use the robot mcp plugin to understand what actions what actions are available to the robot. "
        + " this is the current field data, the blue object stands for the robot, the red object stands for the goal. "
        + json.dumps(data['detection_result'])
        + "the robot is facing east. treat the left bottom corner as the origin (0,0), the x axis is the east direction, and the y axis is the north direction. "
        + ''' 
''' ,
    )

    # await test_shared.mcp.connect()

    agent = AzureAIAgent(
        client=test_shared.project_client,
        definition=agentdef,
        plugins=[test_shared.mcp],  # Add the plugin to the agent
        
    )

    # Create thread for communication
    thread = None

    async for response in agent.invoke(
                        messages=
'describe the current field data, the blue object stands for the robot, the red object stands for the goal. ',
                        thread=thread,
                    ):
        print(f"# {response.name}: {response}")
        thread = response.thread

