from semantic_kernel.connectors.mcp import MCPStdioPlugin
from test_shared import robotData
from robot_agent_orchestrator import run_step0
from robot_agent_observer import run_step1
from robot_agent_planner import run_step2
from robot_agent_controller import run_step3
from robot_agent_judge import run_step4
import asyncio
import test_shared


async def main():
    lego_robot_mcp = MCPStdioPlugin(
            name="robotmcp",
            description="Al Foundry Agents and run query, call this plugin.",
            command="node",
            args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\typescript\\build\\index.js"],
            env={
                "PROJECT_CONNECTION_STRING": "",
                "DEFAULT_ROBOT_ID": "robot_b"
            },
        )
    await lego_robot_mcp.connect()
    
    test_shared.mcp = lego_robot_mcp
    test_shared.thread = None
    robotData.step0_img_path = "D:/gh-repo/lego-agent/testdata/r1.jpg"

    # robotData.runid = ""
    # robotData.step0_img_path = "D:/gh-repo/lego-agent/testdata/step/step0-photo.jpg"
    robotData.step0_img_path = "D:/gh-repo/lego-agent/testdata/r1.jpg"

    # print("\033[93m \r\n--------------------- run_step1 --------------------- \033[0m")
    # await run_step1()
    # await run_step4()

    # print("\033[93m \r\n--------------------- run_step2 --------------------- \033[0m")
    # await run_step2()
    
    # print("\033[93m \r\n--------------------- run_step3 --------------------- \033[0m")
    # await run_step3()
    
    # robotData.step0_img_path = "D:/gh-repo/lego-agent/testdata/r4.jpg"
    # print("\033[93m \r\n--------------------- run_step1 --------------------- \033[0m")
    # await run_step1()
    # await run_step4()

    robotData.step0_img_path = "D:/gh-repo/lego-agent/testdata/r6.jpg"
    print("\033[93m \r\n--------------------- run_step1 --------------------- \033[0m")
    await run_step1()
    await run_step4()

    await lego_robot_mcp.close()

if __name__ == "__main__":
    asyncio.run(main())

