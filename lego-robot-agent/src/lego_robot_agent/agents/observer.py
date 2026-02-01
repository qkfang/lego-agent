"""
LEGO Observer Agent - Captures and analyzes the robot field state.
"""

import json
import requests
from typing import TYPE_CHECKING
from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared

if TYPE_CHECKING:
    from ..context import AgentContext

# Module-level context reference for the ai_function decorator
_observer_context: "AgentContext" = None


async def _process_image(context: "AgentContext"):
    """Process an image and return field data with detection results."""
    from ..models import RoboProcessArgs
    from ..detection import run_detection
    
    robot_data = context.robot_data
    args = RoboProcessArgs()
    args.image_path = robot_data.step0_img_path()
    args.method = "color"
    args.templates = None
    args.target_objects = []
    args.confidence = 0.5
    args.output = robot_data.step1_analyze_json()
    args.visualize = robot_data.step1_analyze_img()
    args.pixels_per_unit = 1.0
    args.no_display = True
    args.no_preprocessing = False

    detection_result = run_detection(args)

    print(f"Image: " + robot_data.step1_analyze_img())
    
    # Try to save image blob if storage is available
    blob = None
    try:
        from lego_api.util.storage import save_image_binary_blobs
        img_file = open(robot_data.step1_analyze_img(), "rb")
        blob = await save_image_binary_blobs(img_file)
    except ImportError:
        # Storage not available, use local path
        blob = robot_data.step1_analyze_img()

    field_data = {"detection_result": detection_result, "blob": blob}
    robot_data.field_data = field_data
    return field_data


@ai_function(description="Get the current state of the robot field by capturing an image via camera")
async def get_field_state_by_camera() -> str:
    """
    Returns analysis data of the current state of the robot field by capturing an image or photo or camera
    """
    global _observer_context
    context = _observer_context
    
    if context is None:
        return json.dumps({"error": "Observer context not initialized"})
    
    if context.notify_callback is not None:
        await context.notify(
            id="text_update",
            subagent='lego-observer',
            status="Field analysis started",
            information="Requesting field photo from camera.",
        )
    
    # Use local file if is_test is True, otherwise use camera
    if context.is_test:
        # Mock mode: use sample images
        import os
        from pathlib import Path
        
        # Find project root by looking for a marker file (e.g., sample directory)
        current_file = Path(__file__).resolve()
        project_root = None
        
        # Try to find project root by going up directories
        for parent in current_file.parents:
            sample_dir = parent / "sample"
            if sample_dir.exists() and sample_dir.is_dir():
                project_root = parent
                break
        
        # Fallback: use environment variable if set
        if project_root is None and os.getenv("LEGO_PROJECT_ROOT"):
            project_root = Path(os.getenv("LEGO_PROJECT_ROOT"))
        
        # Last resort: try relative path from current file
        if project_root is None:
            project_root = current_file.parents[4]  # 4 levels up from observer.py
        
        if context.test_count == 1:
            image_file = project_root / "sample" / "step1.jpg"
        else:
            image_file = project_root / "sample" / "step2.jpg"

        print(f'Mock mode: context.test_count={context.test_count}, using image: {image_file}')
        with open(image_file, "rb") as f:
            img_data = f.read()

        context.increment_test_count()
    else:
        url = "http://192.168.0.50:5000/photo"
        response = requests.get(url)
        img_data = response.content

    with open(context.robot_data.step0_img_path(), "wb") as f:
        f.write(img_data)

    data = await _process_image(context)
    return json.dumps(data)


class LegoObserverAgent:
    """LEGO Observer Agent using Microsoft Agent Framework."""
    
    AGENT_NAME = "lego-observer"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the observer agent using Microsoft Agent Framework with tools.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        global _observer_context
        self._context = context
        _observer_context = context
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model="gpt-4o",
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
'''
                ),
            )
        
        self.agent = ChatAgent(
            chat_client=AzureAIAgentClient(
                    project_endpoint=shared.AZURE_AI_PROJECT_ENDPOINT,
                    model_deployment_name=shared.AZURE_OPENAI_DEPLOYMENT,
                    agent_name=agentdef.name,
                    credential=shared.credential,
                ),
            name=self.AGENT_NAME,
            description="Captures and analyzes the robot field state",
            tools=[get_field_state_by_camera]
        )

    async def exec(self, message: str) -> str:
        """Execute the observer agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
