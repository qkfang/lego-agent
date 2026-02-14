from agent_framework import MCPStdioTool
from lego_robot_agent.agents import LegoControllerAgent
from lego_robot_agent.context import AgentContext
import asyncio
import lego_robot_agent.shared as shared

async def main():
    shared.isTest = False
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]
    
    async with MCPStdioTool(
        name="mcp_legorobot_action",
        command="node",
        args=[shared.mcp_server_path],
        # env={"IS_MOCK": "true"},
        load_prompts=False,
    ) as mcp_legorobot_action:
        
        context = AgentContext(
            azure_client=shared.azure_client,
            mcp_session=None,
            mcp_legorobot_action=[mcp_legorobot_action],
            robot_data=shared.robotData,
            is_test=True
        )
        
        legoControllerAgent = LegoControllerAgent()
        await legoControllerAgent.init(context)
        await legoControllerAgent.exec('move forward 20 cm, turn right 90 degrees, and do a full circle')
        
        if hasattr(legoControllerAgent.agent, 'chat_client'):
            await legoControllerAgent.agent.chat_client.close()
    
    # Clean up project client
    await shared.project_client.close()

if __name__ == "__main__":
    asyncio.run(main())

