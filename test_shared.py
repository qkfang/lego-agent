import datetime
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

mcp = None

class RobotData:
    def __init__(self):
        self.root = "D:/gh-repo/lego-agent/api/temp"
        self.runid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

        # step 0
        self.step0_img_path = None

        # step 1
        self.step1_analyze_img = None
        self.step1_analyze_json = None

        # step 2
        self.step2_plan_json = None


robotData = RobotData()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="eastus2.api.azureml.ms;79b9afaa-2d77-4d1e-b902-98df2bd3b3d6;rg-agent100;mamimezf5xgqov-aiproject" # os.environ["PROJECT_CONNECTION_STRING"]
)

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "telemetry-console-quickstart"})
