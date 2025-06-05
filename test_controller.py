from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent, AzureAIAgentSettings

import test_shared
from test_shared import robotData


async def run_step3():

    with open(robotData.step2_plan_json, "r", encoding="utf-8") as file:
        contents = file.read()

    agentdef = await test_shared.project_client.agents.create_agent(
        model="gpt-4o" , #""os.environ["MODEL_DEPLOYMENT_NAME"],
        name="lego-api333",
        instructions="You are robot action connter. need to follow the plan to control the robot to action. do one step at a time and wait for earlier action to complete. "
        + contents
        ,
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
                        messages='Follow the plan to make robot action.',
                        thread=thread,
                    ):
        print(f"# {response.name}: {response}")
        thread = response.thread

