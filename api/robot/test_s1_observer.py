import json
import shared
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from semantic_kernel.functions import kernel_function
from shared import robotData
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from robot.robotmodel import RobotData, RoboProcessArgs
from agent.storage import save_image_binary_blobs
from robot.objectdetector import run 



async def processImage(robotData: RobotData):
    args = RoboProcessArgs()
    args.image_path = robotData.step0_img_path
    args.method = "color"
    args.templates = None
    args.target_objects = ["blue", "red"]
    args.confidence = 0.5
    args.output = robotData.step1_analyze_json()
    args.visualize = robotData.step1_analyze_img()
    args.pixels_per_unit = 1.0
    args.no_display = True
    args.no_preprocessing = True
    detection_result = run(args)

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


        if(robotData.sequence == 0):
            robotData.step0_img_path = 'D:/gh-repo/lego-agent/testdata/r1.jpg'
        else:
            robotData.step0_img_path = 'D:/gh-repo/lego-agent/testdata/r6.jpg'

        robotData.sequence += 1
        print("robotData.step0_img_path:" + robotData.step0_img_path)

        data = await processImage(robotData)
        print (f"get_field_state_by_camera: {robotData.field_data}")

        # await test_shared.chat.add_chat_message(message=ChatMessageContent(role="assistant", content=json.dumps(robotData.field_data, indent=2)))

        return data
        

async def run_step1(agentOnly: bool = False):

    
    agentdef = await shared.project_client.agents.create_agent(
        model="gpt-4o",
        name="lego-observer",
        temperature=0,
        instructions=
'''
You are robot field observer. 
never ask for an photo, you must get it yourself.

EVERY SINGLE TIME, you must use a camera to capture field photo.
You can get field state from the photo each time anytime.

the robot is facing east. treat the left bottom corner as the origin (0,0)
the x axis is the east direction, and the y axis is the north direction.

Only return analysis data in json format in your response. dont return any other text or explanation.
'''
    )

    agent = AzureAIAgent(
        client=shared.project_client,
        definition=agentdef,
        plugins=[FieldStatePlugin],
    )

    if(agentOnly):
        return agent

#     response = await agent.get_response(
#         messages=
# 'describe the current field data, the blue object stands for the robot, the red object stands for the goal. ',
#         thread=shared.thread,
#     )
#     print(f"# {response.name}: {response}")
#     test_shared.thread = response.thread

