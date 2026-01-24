"""
LEGO Judger Agent - Evaluates goal completion.
"""

from typing import TYPE_CHECKING
from agent_framework import ChatAgent

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoJudgerAgent:
    """LEGO Judger Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-judger"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the judger agent using Microsoft Agent Framework.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        self._context = context
        
        self.agent = ChatAgent(
            chat_client=context.azure_client,
            name=self.AGENT_NAME,
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

    async def exec(self, message: str) -> str:
        """Execute the judger agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
