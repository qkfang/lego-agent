import json
import test_shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from api.agent.agents import processImage
from test_shared import robotData


async def run_step0():

    data = await processImage(robotData)
    # print(json.dumps(data, indent=2))

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o",
        name="lego-api333",
        instructions=
'''
You are robot orchestrator. 

# rule
first you need to analyze the current field data, and decide if the goal is already achieved.
if the goal is achieved, then you can stop the action and return the result.

'''
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

