"""
LEGO Controller Agent - Executes physical robot actions via MCP tools.
"""

from typing import TYPE_CHECKING
from agent_framework import ChatAgent

if TYPE_CHECKING:
    from ..context import AgentContext


class LegoControllerAgent:
    """LEGO Controller Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-controller"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the controller agent using Microsoft Agent Framework with MCP tools.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        self._context = context
        
        # Get MCP tools from context if available
        tools = []
        if context.mcp_session is not None:
            tools = context.mcp_tools if context.mcp_tools else []
        
        self.agent = ChatAgent(
            chat_client=context.azure_client,
            name=self.AGENT_NAME,
            instructions='''
You are robot controller agent. need to follow the plan to control the robot to action. 
do one step at a time and wait for earlier action to complete. 
MUST run all the steps using robot function and action physically without skipping any step.
dont ask for any confirmation, just follow the plan step by step.

You do not know if the robot action is successful or not, and you should not only say the action has been done.
NEVER say 'task is completed' or 'successfully completed the task', just say the action is done.
NEVER repeat other agent's response, just provide your own answer.
After performing all actions, say that 'detection_result' is no longer valid, need to ask observer agent to provide the latest field data.
''',
            tools=tools,
            description="Robot controller that executes physical robot actions"
        )

    async def exec(self, message: str) -> str:
        """Execute the controller agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
