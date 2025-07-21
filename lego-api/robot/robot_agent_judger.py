import shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent


class LegoJudgerAgent:
    agent = None
    agentName = "lego-judger"

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
You are robot judger agent. 
You need to decide if the goal is already achieved based on the current field data and the goal.
if distance to Red Object is less than 180 pixels, the robot has successfully grabbed the red object and meet the goal.

You must provide an answer in response by saying **goal completed** or **goal failed**. Also include the reason for your decision.
NEVER repeat other agent's response, just provide your own answer.
'''
        )

        self.agent = AzureAIAgent(
            client=shared.project_client,
            definition=agentdef,
            plugins=[],
        )



    async def exec(self, message: str):
        response = await self.agent.get_response(
                                        messages= message, 
                                        thread=shared.thread
                                    )
        print(f"# {response.name}: {response.content}")
        return str(response)
