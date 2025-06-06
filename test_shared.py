from api.robot.robotmodel import RobotData
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="eastus2.api.azureml.ms;79b9afaa-2d77-4d1e-b902-98df2bd3b3d6;rg-agent100;mamimezf5xgqov-aiproject" # os.environ["PROJECT_CONNECTION_STRING"]
)

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "telemetry-console-quickstart"})
mcp = None
thread = None
robotData = RobotData()
