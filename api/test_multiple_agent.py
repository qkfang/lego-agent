import asyncio
import agenttest.test_shared
from agenttest.test_shared import robotData
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.contents import AuthorRole
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.contents import AuthorRole
from agenttest.test_s0_orchestrator import run_step0
from agenttest.test_s1_observer import run_step1
from agenttest.test_s2_planner import run_step2
from agenttest.test_s3_controller import run_step3
from agenttest.test_s4_judge import run_step4


class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "goal completed" in history[-1].content.lower()

TASK = "move the blue robot (blue object) to the red object, and stop when the robot is close enough to the red object. " \


async def main():
      
    lego_robot_mcp = MCPStdioPlugin(
            name="AIFoundryAgents",
            description="Al Foundry Agents and run query, call this plugin.",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\typescript\\build\\index.js"],
            env={
                "PROJECT_CONNECTION_STRING": "eastus2.api.azureml.ms;79b9afaa-2d77-4d1e-b902-98df2bd3b3d6;rg-agent100;mamimezf5xgqov-aiproject",
                "DEFAULT_ROBOT_ID": "robot_b"
            },
        )
    await lego_robot_mcp.connect()
    
    agenttest.test_shared.mcp = lego_robot_mcp
    agenttest.test_shared.thread = None
  
    agentOrchestrator = await run_step0(agentOnly=True)
    agentObserver = await run_step1(agentOnly=True)
    agentPlanner = await run_step2(agentOnly=True)
    agentController = await run_step3(agentOnly=True)
    agentJudge = await run_step4(agentOnly=True)

    # 5. Place the agents in a group chat with a custom termination strategy
    chat = AgentGroupChat(
        agents=[agentOrchestrator, agentObserver, agentPlanner, agentController, agentJudge],
        termination_strategy=ApprovalTerminationStrategy(agents=[agentJudge], maximum_iterations=10),
    )
    agenttest.test_shared.chat = chat

    try:

        await chat.add_chat_message(message=TASK)
        print(f"# {AuthorRole.USER}: '{TASK}'")
        async for content in chat.invoke():
            print("\033[93m \r\n--------------------- agent --------------------- \033[0m")
            print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
        

    finally:
        await chat.reset()
        
        await agenttest.test_shared.project_client.agents.delete_agent(agentOrchestrator.id)
        await agenttest.test_shared.project_client.agents.delete_agent(agentObserver.id)
        await agenttest.test_shared.project_client.agents.delete_agent(agentPlanner.id)
        await agenttest.test_shared.project_client.agents.delete_agent(agentController.id)
        await agenttest.test_shared.project_client.agents.delete_agent(agentJudge.id)



if __name__ == "__main__":
    asyncio.run(main())


