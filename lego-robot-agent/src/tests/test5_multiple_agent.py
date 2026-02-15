import asyncio
import lego_robot_agent.shared as shared
from agent_framework import MCPStdioTool
from lego_robot_agent import LegoAgent
from lego_robot_agent.context import AgentContext

async def main():

    shared.isTest = True
    shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]
    
    async with MCPStdioTool(
        name="robot_mcp",
        command="node",
        args=[shared.mcp_server_path],
        env={"IS_MOCK": "true"},
        load_prompts=False,
    ) as mcp_tool:

        context = AgentContext(
            azure_client=shared.azure_client,
            mcp_session=None, 
            mcp_legorobot_action=[mcp_tool], 
            robot_data=shared.robotData,
            is_test=True
        )

        legoAgent = LegoAgent(context)

        await legoAgent.init()
        await legoAgent.run('grab bowser a coke and go back.')
        
        for agent in [legoAgent._orchestrator, legoAgent._observer, legoAgent._planner, 
                      legoAgent._controller, legoAgent._judge]:
            if hasattr(agent, 'agent') and hasattr(agent.agent, 'chat_client'):
                await agent.agent.chat_client.close()
    
    await shared.project_client.close()

if __name__ == "__main__":
    asyncio.run(main())


