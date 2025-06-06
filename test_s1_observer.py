import json
import test_shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from api.agent.agents import processImage
from test_shared import robotData


async def run_step1():

    await processImage(robotData)

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o",
        name="lego-api333",
        instructions=
'''
You are robot field observer. 

# rule
first you need to analyze the current field data.

# field position
the robot is facing east. 
treat the left bottom corner as the origin (0,0)
the x axis is the east direction, and the y axis is the north direction.

this is the current field data.
''' + json.dumps(robotData.field_data),
    )

    agent = AzureAIAgent(
        client=test_shared.project_client,
        definition=agentdef,
        plugins=[test_shared.mcp],
    )

    response = await agent.get_response(
        messages=
'describe the current field data, the blue object stands for the robot, the red object stands for the goal. ',
        thread=test_shared.thread,
    )
    print(f"# {response.name}: {response}")
    test_shared.thread = response.thread

