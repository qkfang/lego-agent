import json
import shared
from agent_framework import ChatAgent


class LegoOrchestratorAgent:
    """LEGO Orchestrator Agent using Microsoft Agent Framework."""
    agent: ChatAgent = None
    agentName = "lego-orchestrator"

    def __init__(self):
        self.agent = None

    async def init(self):
        """Initialize the orchestrator agent using Microsoft Agent Framework."""
        
        # Create agent using the Azure OpenAI Responses client
        self.agent = ChatAgent(
            chat_client=shared.azure_client,
            name=self.agentName,
            instructions='''
You are robot orchestrator agent. 
Always starting with analyzing the current field data.
When judger agent has already determined that the goal is completed or failed, you must end the conversation by saying 'agents have completed actions' and provide a summary of past activities.
It's always good to ask user to check the final result in the end.
''',
            # Agent Framework supports additional configuration
            description="Robot orchestrator that coordinates the multi-agent workflow"
        )

    async def exec(self, message: str):
        """Execute the orchestrator agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.agentName}: {response}")
        return str(response)


legoOrchestratorAgent = LegoOrchestratorAgent()
