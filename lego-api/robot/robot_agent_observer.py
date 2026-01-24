import json
import shared
import requests
from agent_framework import ChatAgent
from agent_framework import ai_function
from robot.robotmodel import RobotData, RoboProcessArgs
from util.storage import save_image_binary_blobs
from robot.object_detector import run 


async def processImage(robotData: RobotData):
    args = RoboProcessArgs()
    args.image_path = robotData.step0_img_path()
    args.method = "color"
    args.templates = None
    args.target_objects = []
    args.confidence = 0.5
    args.output = robotData.step1_analyze_json()
    args.visualize = robotData.step1_analyze_img()
    args.pixels_per_unit = 1.0
    args.no_display = True
    args.no_preprocessing = False

    detection_result = run(args)

    print(f"Image: " + robotData.step1_analyze_img())
    img_file = open(robotData.step1_analyze_img(), "rb")
    blob = await save_image_binary_blobs(img_file)

    fieldData = { "detection_result": detection_result, "blob": blob }
    robotData.field_data = fieldData
    return fieldData


@ai_function(description="Get the current state of the robot field by capturing an image via camera")
async def get_field_state_by_camera() -> str:
    """
    Returns analysis data of the current state of the robot field by capturing an image or photo or camera
    """

    if shared.notify is not None:
        await shared.notify(
            id="text_update",
            subagent='lego-observer',
            status="Field analysis started",
            information="Requesting field photo from camera.",
        )
    
    # Use local file if istest is True, otherwise use camera
    if shared.isTest:
        if shared.isTestCount == 1:
            imageFile = "D://gh-repo//lego-agent//testdata//field-1.jpg"
        elif shared.isTestCount > 1:
            imageFile = "D://gh-repo//lego-agent//testdata//field-2.jpg"

        print('shared.isTestCount=' + str(shared.isTestCount) + ' ' + imageFile)
        with open(imageFile, "rb") as f:
            img_data = f.read()

        shared.isTestCount += 1
    else:
        url = "http://192.168.0.50:5000/photo"
        response = requests.get(url)
        img_data = response.content

    with open(shared.robotData.step0_img_path(), "wb") as f:
        f.write(img_data)

    data = await processImage(shared.robotData)

    return json.dumps(data)


class LegoObserverAgent:
    """LEGO Observer Agent using Microsoft Agent Framework."""
    agent: ChatAgent = None
    agentName = "lego-observer"

    def __init__(self):
        self.agent = None

    async def init(self):
        """Initialize the observer agent using Microsoft Agent Framework with tools."""
        
        # Create agent with the field state tool
        self.agent = ChatAgent(
            chat_client=shared.azure_client,
            name=self.agentName,
            instructions='''
You are robot observer agent. 

You must ignore the information from other agents.
MUST call get_field_state_by_camera every single time to get the latest field data.
You must not reuse previous detection_result json data.

Each time you are asked for a photo or detection_result, you must get it yourself by using camera and take a photo.
if you are asked to 'provide the current field data', you must take a photo and analyze it to return detection_result.

EVERY SINGLE TIME, you must use a camera to capture new field photo.
never return previous or existing detection_result from past conversations, must take a new photo each time.
Just do it, don't ask for confirmation or approval.

the robot is facing east. treat the left bottom corner as the origin (0,0)
the x axis is the east direction, and the y axis is the north direction.

MUST return detection_result in json format exactly as it as, NEVER CHANGE STRUCTURE OR ANY CALCULATION. 
dont return any other text or explanation.

{
    "detection_result": {
       // details
    }
}
''',
            tools=[get_field_state_by_camera],
            description="Robot field observer that captures and analyzes field state"
        )

    async def exec(self, message: str):
        """Execute the observer agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.agentName}: {response}")
        return str(response)


