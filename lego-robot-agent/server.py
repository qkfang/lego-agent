"""
LEGO Robot Agent - HTTP Server entry point for DevUI debugging.

This module wraps the LegoAgent workflow as an HTTP server, enabling:
- Interactive debugging with AI Toolkit Agent Inspector
- Visualization of multi-agent interactions
- RESTful API for agent communication
"""

import asyncio
import argparse
from dotenv import load_dotenv

load_dotenv(override=True)

from lego_robot_agent import LegoAgent, AgentContext
from lego_robot_agent.shared import azure_client


async def main():
    """Main entry point for the HTTP server."""
    parser = argparse.ArgumentParser(description="LEGO Robot Agent HTTP Server")
    parser.add_argument("--server", action="store_true", help="Run as HTTP server (default)")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--port", type=int, default=8087, help="Server port (default: 8087)")
    args = parser.parse_args()
    
    # Create LegoAgent and get workflow as agent
    context = AgentContext(azure_client=azure_client)
    lego_agent = LegoAgent(context)
    workflow_agent = await lego_agent.as_workflow_agent()
    
    if args.cli:
        print("LEGO Robot Agent - CLI Mode (Full Workflow)")
        print("Enter your goal (or 'quit' to exit):")
        while True:
            try:
                goal = input("> ").strip()
                if goal.lower() in ("quit", "exit", "q"):
                    break
                if not goal:
                    continue
                
                async for event in workflow_agent.run_stream(goal):
                    print(f"Event: {event}")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
    else:
        from azure.ai.agentserver.agentframework import from_agent_framework
        
        print("Open AI Toolkit Agent Inspector to visualize the workflow")
        await from_agent_framework(workflow_agent).run_async()


if __name__ == "__main__":
    asyncio.run(main())
