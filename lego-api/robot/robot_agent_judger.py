import shared
from agent_framework import ChatAgent


class LegoJudgerAgent:
    """LEGO Judger Agent using Microsoft Agent Framework."""
    agent: ChatAgent = None
    agentName = "lego-judger"

    def __init__(self):
        self.agent = None

    async def init(self):
        """Initialize the judger agent using Microsoft Agent Framework."""
        
        # Create agent for judging goal completion
        self.agent = ChatAgent(
            chat_client=shared.azure_client,
            name=self.agentName,
            instructions='''
You are robot judger agent. 

You need to decide if the goal is already achieved based on the current field data and the goal.
when the distance between coke and bowser is less than 180 pixels, it means that the robot has delievered the coke to the bowser successfully.
robot position should not be considered.

You must provide an answer in response by saying **goal completed** or **goal failed**. Also include the reason for your decision.
NEVER repeat other agent's response, just provide your own answer.
''',
            description="Robot judger that evaluates goal completion"
        )

    async def exec(self, message: str):
        """Execute the judger agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.agentName}: {response}")
        return str(response)
