from lego_robot_agent.models import RobotData
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential, AzureCliCredential
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
import os
from dotenv import load_dotenv
load_dotenv()

# Microsoft Agent Framework - uses Azure OpenAI directly
# The agent-framework package provides workflow orchestration
from agent_framework.azure import AzureOpenAIChatClient

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://legobot-foundry.openai.azure.com/")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")


credential=AzureCliCredential()

# Create the Azure OpenAI Chat client for agent creation
azure_client = AzureOpenAIChatClient(
    endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    credential=credential,
)

# Get Azure AI Foundry project endpoint from environment
AZURE_AI_PROJECT_ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", os.environ.get("PROJECT_CONNECTION_STRING", ""))

project_client = AIProjectClient(
    endpoint=AZURE_AI_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "lego-telemetry"})
robotData = RobotData()
foundryAgents = []

notify = None
chat = None
workflow = None  # Workflow for multi-agent orchestration
mcprobot = None
robotmcptools = None
sessionrt = None
thread = None
lastImage = None

isTest = False
isTestCount = 1
