import json
import shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from shared import robotData


async def run_step4(agentOnly: bool = False):

    data = ''
    if not agentOnly:
        data = robotData.step1_analyze_json_data()

    agentdef = await shared.project_client.agents.create_agent(
        model="gpt-4o",
        name="lego-judge",
        temperature=0,
        instructions=
'''
You are robot judge. 
You need to decide if the goal is already achieved based on the current field data and the goal.
100px in distance is close enough to the goal, so you can consider it as completed.

You must provide an answer in response by saying 'goal completed' or 'goal failed'.

''' + data
    )

    agent = AzureAIAgent(
        client=shared.project_client,
        definition=agentdef,
        plugins=[],
    )

    if(agentOnly):
        return agent

#     response = await agent.get_response(
#         messages=
# '''
# goal meet? 
# ''',
#         thread=shared.thread,
#     )
#     print(f"# {response.name}: {response}")

