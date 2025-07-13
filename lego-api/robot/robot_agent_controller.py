import shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent


class LegoControllerAgent:
    agent = None
    agentName = "lego-controller"

    def __init__(self):
        self.agent = None

    async def init(self):
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.agentName), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_agent(
                model="gpt-4o",
                name=self.agentName,
                temperature=0,
                instructions=
'''
You are robot controller agent. need to follow the plan to control the robot to action. 
do one step at a time and wait for earlier action to complete. 
MUST run all the steps using robot function and action physically without skipping any step.
dont ask for any confirmation, just follow the plan step by step.

You do not know if the robot action is successful or not, and you should not only say the action has been done.
NEVER say 'task is completed' or 'successfully completed the task', just say the action is done.
NEVER repeat other agent's response, just provide your own answer.
after performing all actions, say that 'detection_result' is no longer valid, need to ask observer agent to provide the latest field data.
'''
            )

        self.agent = AzureAIAgent(
            client=shared.project_client,
            definition=agentdef,
            plugins=[shared.mcprobot],
        )


    async def exec(self, message: str):
        response = await self.agent.get_response(
                                        messages= message, 
                                        thread=shared.thread
                                    )
        print(f"# {response.name}: {response.content}")
        return str(response)


