import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole
from dotenv import load_dotenv

load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str= os.environ["PROJECT_CONNECTION_STRING"]
)


# Create agent with AI search tool and process assistant run
with project_client:
    agents = project_client.agents.list_agents(limit=100)
  
    for agent in agents.data:
        # # Delete the assistant when done
        project_client.agents.delete_agent(agent.id)
        print("Deleted agent: " + agent.id)
