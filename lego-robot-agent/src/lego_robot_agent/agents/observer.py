"""
LEGO Observer Agent - Captures and analyzes the robot field state.
"""

import json
import requests
from typing import TYPE_CHECKING
from pathlib import Path
from agent_framework import ai_function
from agent_framework.declarative import AgentFactory
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
        if context.test_count == 1:
            image_file = "D://gh-repo//lego-agent//testdata//field-1.jpg"
        elif context.test_count > 1:
            image_file = "D://gh-repo//lego-agent//testdata//field-2.jpg"

        print('context.test_count=' + str(context.test_count) + ' ' + image_file)
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
        self.agent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        """
        Initialize the observer agent using declarative YAML with tools.
        
        Args:
            context: The agent context with Azure client and dependencies
        """
        global _observer_context
        self._context = context
        _observer_context = context
        
        # Get the path to the YAML file
        prompts_dir = Path(__file__).parent.parent / "prompts"
        yaml_path = prompts_dir / "observer.yaml"
        
        # Create agent from declarative YAML using AgentFactory with custom tools
        agent_factory = AgentFactory(
            client_kwargs={"credential": shared.credential},
            bindings={"get_field_state_by_camera": get_field_state_by_camera}
        )
        self.agent = agent_factory.create_agent_from_yaml_path(yaml_path)

    async def exec(self, message: str) -> str:
        """Execute the observer agent with a message."""
        response = await self.agent.run(message)
        print(f"# {self.AGENT_NAME}: {response}")
        return str(response)
