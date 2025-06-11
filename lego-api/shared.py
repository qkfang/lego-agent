from robot.robotmodel import RobotData
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from robot.robot_agent import LegoAgent
import os
from dotenv import load_dotenv
load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "lego-telemetry"})
robotData = RobotData()
legoAgent = LegoAgent()
foundryAgents = []

notify = None
chat = None
mcp = None
realtime1 = None
mcptools = None
thread = None

isTest = True
isTestCount = 1
