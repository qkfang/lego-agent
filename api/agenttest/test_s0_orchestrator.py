import json
import agenttest.test_shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from agenttest.test_shared import robotData


async def run_step0(agentOnly: bool = False):

    agentdef = await agenttest.test_shared.project_client.agents.create_agent(
        model="gpt-4o",
        name="lego-ochestrator",
        temperature=0.2,
        instructions=
'''
You are robot orchestrator. 

Always starting with analyzing the current field data, and decide if the goal is already achieved.

if the goal is achieved, then you can stop the action and return the result.
if the goal is failed or not achieved, need to analyze the field data again.

'''
    )

    agent = AzureAIAgent(
        client=agenttest.test_shared.project_client,
        definition=agentdef,
        plugins=[],
    )

    if(agentOnly):
        return agent

    response = await agent.get_response(
        messages=
'describe the current field data, the blue object stands for the robot, the red object stands for the goal. ',
        thread=agenttest.test_shared.thread,
    )
    print(f"# {response.name}: {response}")
    agenttest.test_shared.thread = response.thread

