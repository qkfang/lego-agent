from robot.robotmodel import RobotData
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

# Create the Azure OpenAI Chat client for agent creation
azure_client = AzureOpenAIChatClient(
    endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    credential=AzureCliCredential(),
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
