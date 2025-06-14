import json
import shared
import requests
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from semantic_kernel.functions import kernel_function
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from robot.robotmodel import RobotData, RoboProcessArgs
from util.storage import save_image_binary_blobs
from robot.object_detector import run 


async def processImage(robotData: RobotData):
    args = RoboProcessArgs()
    args.image_path = robotData.step0_img_path()
    args.method = "color"
    args.templates = None
    args.target_objects = ["robot", "red", "yellow"]
    args.confidence = 0.5
    args.output = robotData.step1_analyze_json()
    args.visualize = robotData.step1_analyze_img()
    args.pixels_per_unit = 1.0
    args.no_display = True
    args.no_preprocessing = True
    detection_result = run(args)

    print(f"Image: " + robotData.step1_analyze_img())
    img_file = open(robotData.step1_analyze_img(), "rb")
    blob = await save_image_binary_blobs(img_file)

    fieldData = { "detection_result": detection_result, "blob": blob }
    robotData.field_data = fieldData
    return fieldData


class FieldStatePlugin:
    """
    Description: Capture field state via camera or photo as analysis data.
    """

    @kernel_function(
        description="the current state of the robot field by capturing an image or photo or camera",
        name="get_field_state_by_camera",
    )
    async def get_field_state_by_camera() -> str:
        """
        Returns analysis data of the current state of the robot field by capturing an image or photo or camera
        """

        if shared.notify is not None:
            await shared.notify(
                id="text_update",
                subagent = 'lego-observer',
                status="Field analysis started",
                information="Requesting field photo from camera.",
            )
        
        # Use local file if istest is True, otherwise use camera
        if shared.isTest:
            if(shared.isTestCount == 1):
                imageFile = "D://gh-repo//lego-agent//testdata//field-1.jpg"
            elif(shared.isTestCount > 1):
                imageFile = "D://gh-repo//lego-agent//testdata//field-2.jpg"
            # if(shared.isTestCount == 2):
            #     imageFile = "D://gh-repo//lego-agent//testdata//field-1.jpg"

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
        # print (f"get_field_state_by_camera: {shared.robotData.field_data}")

        return data


class LegoObserverAgent:
    agent = None
    agentName = "lego-observer"

    def __init__(self):
        self.agent = None


    async def init(self):

        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.agentName), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_agent(
                model="gpt-4o",
                name=self.agentName,
                temperature=0,
                instructions=
'''
You are robot field observer. 
never ask for an photo, you must get it yourself.

EVERY SINGLE TIME, you must use a camera to capture field photo.
You can get field state from the photo each time anytime.

the robot is facing east. treat the left bottom corner as the origin (0,0)
the x axis is the east direction, and the y axis is the north direction.

MUST return detection_result in json format exactly as it as, NEVER CHANGE STRUCTURE OR ANY CALCULATION. 
dont return any other text or explanation.
'''
        )

        self.agent = AzureAIAgent(
            client=shared.project_client,
            definition=agentdef,
            plugins=[FieldStatePlugin],
            
        )


    async def exec(self, message: str):
        response = await self.agent.get_response(
                                        messages= message, 
                                        thread=shared.thread
                                    )
        print(f"# {response.name}: {response.content}")
        return str(response)


