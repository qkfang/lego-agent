import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="eastus2.api.azureml.ms;79b9afaa-2d77-4d1e-b902-98df2bd3b3d6;rg-agent100;mamimezf5xgqov-aiproject" # os.environ["PROJECT_CONNECTION_STRING"]
)


async def create_agent(agent_names, agentname: str, agentinstruct: str):
    
    if agentname not in agent_names:
        project_client.agents.create_agent(
            model="gpt-4o" , #""os.environ["MODEL_DEPLOYMENT_NAME"],
            name=agentname,
            instructions=agentinstruct,
        )

import asyncio

async def main():
    with project_client:
        agents = project_client.agents.list_agents(limit=100)
        agent_names = [agent.name for agent in agents.data]
        
        await create_agent(agent_names, 'lego-observer', '''
You are an observer agent for a LEGO robot. Your task is to monitor the robot's actions and provide feedback on its performance. 
You will receive updates from the robot and should respond with observations and suggestions for improvement. Do not perform any actions yourself, just observe and report.
            ''')
      
        await create_agent(agent_names, 'lego-planner', '''
You are a planner agent for a LEGO robot. Your task is to create plans and strategies for the robot to follow. 
You will receive requests for planning and should respond with detailed plans that the robot can execute. Do not perform any actions yourself, just plan and strategize.
you can perform actions like move(), turn(), beep(), action(command) to communicate with the robot.
return 
            ''')
        await create_agent(agent_names, 'lego-robot', '''
You are a LEGO robot agent. Your task is to execute plans and perform actions based on the instructions you receive. 
You will receive commands from the planner agent and should respond with updates on your actions and any observations you make during execution. Do not create plans yourself, just execute them.
you can perform actions like move(), turn(), beep(), action(command) to communicate with the robot. 
perform one action at a time and wait for the next command.
              ''')

if __name__ == "__main__":
    asyncio.run(main())
