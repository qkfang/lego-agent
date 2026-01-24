import shared
from agent_framework import ChatAgent


class LegoControllerAgent:
    """LEGO Controller Agent using Microsoft Agent Framework."""
    agent: ChatAgent = None
    agentName = "lego-controller"

    def __init__(self):
        self.agent = None

    async def init(self):
        """Initialize the controller agent using Microsoft Agent Framework with MCP tools."""
        
        # Get MCP tools from shared if available
        tools = []
        if shared.mcprobot is not None:
            tools = shared.robotmcptools if shared.robotmcptools else []
        
        # Create agent with MCP robot tools for physical control
        self.agent = ChatAgent(
            chat_client=shared.azure_client,
            name=self.agentName,
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

    async def exec(self, message: str):
        """Execute the controller agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.agentName}: {response}")
        return str(response)


