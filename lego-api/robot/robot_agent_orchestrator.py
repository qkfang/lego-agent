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
                temperature=0.2,
                instructions=
'''
You are robot orchestrator. 

Always starting with analyzing the current field data, and decide if the goal is already achieved.

if the goal is achieved, then you can stop the action and return the result.
if the goal is failed or not achieved, need to analyze the field data again.
NEVER repeat other agent's response, just provide your own answer.
'''
        )

        self.agent = AzureAIAgent(
            client=shared.project_client,
            definition=agentdef,
            plugins=[],
        )


    async def run_step0(self):
        
        response = await self.agent.get_response(
        messages=
'''
describe the current field data, the blue object stands for the robot, the red object stands for the goal. 
''',
            thread=shared.thread,
        )
        print(f"# {response.name}: {response}")
        shared.thread = response.thread


legoOrchestratorAgent = LegoOrchestratorAgent()
