import agenttest.test_shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from agenttest.test_shared import robotData


async def run_step3(agentOnly: bool = False):

    data = ''
    if not agentOnly:
        data = robotData.step2_plan_json_data()

    agentdef = await agenttest.test_shared.project_client.agents.create_agent(
        model="gpt-4o" , #""os.environ["MODEL_DEPLOYMENT_NAME"],
        name="lego-controller",
        temperature=0,
        instructions=
'''
You are robot action connter. need to follow the plan to control the robot to action. do one step at a time and wait for earlier action to complete. 
dont ask for any confirmation, just follow the plan step by step.
'''
        + data,
    )

    agent = AzureAIAgent(
        client=agenttest.test_shared.project_client,
        definition=agentdef,
        plugins=[agenttest.test_shared.mcp],
    )

    if(agentOnly):
        return agent
    
    response = await agent.get_response(
        messages=
'''
Follow the plan to make robot action.
''',
        thread=agenttest.test_shared.thread,
    )

    print(f"# {response.name}: {response}")

    
