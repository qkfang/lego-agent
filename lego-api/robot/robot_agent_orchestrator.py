import json
import shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent


class LegoOrchestratorAgent:
    agent = None
    agentName = "lego-orchestrator"

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
You are robot orchestrator agent. 
Always starting with analyzing the current field data, and decide if the goal is already achieved.
If judger agent has already answered the goal is completed or failed, you must end the conversation by saying 'agents have completed actions' and provide a summary of past activities and ask human to check.
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


legoOrchestratorAgent = LegoOrchestratorAgent()
