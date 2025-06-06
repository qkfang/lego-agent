import json
import test_shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from api.agent.agents import processImage
from test_shared import robotData


async def run_step4():

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o",
        name="lego-api333",
        instructions=
'''
You are robot judge. 

you need to decide if the goal is already achieved based on the current field data and the goal.

if the goal is achieved, then you can stop the action and return the result.

''' + robotData.step1_analyze_json_data()
    )

    agent = AzureAIAgent(
        client=test_shared.project_client,
        definition=agentdef,
        plugins=[test_shared.mcp],
    )

    response = await agent.get_response(
        messages=
'goal meet? ',
        thread=test_shared.thread,
    )
    print(f"# {response.name}: {response}")

