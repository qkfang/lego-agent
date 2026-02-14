import json
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.models import PromptAgentDefinition
from .. import shared
from ..context import AgentContext
from ..helper.logic import get_field_state_by_camera, _observer_context
from ..type.models import FieldData, DetectionResult


class ObserverChatAgent(ChatAgent):
    """ChatAgent subclass that always returns structured FieldData."""

    async def run(self, messages=None, **kwargs):
        kwargs.setdefault("response_format", FieldData)
        response = await super().run(messages, **kwargs)
        print(f"# lego-observer: {response}")
        return response


class LegoObserverAgent:
    AGENT_NAME = "lego-observer"
    
    def __init__(self):
        self.agent: ChatAgent = None
        self._context: "AgentContext" = None

    async def init(self, context: "AgentContext"):
        from ..helper import logic
        self._context = context
        logic._observer_context = context
        
        agentdef = next((agent for agent in shared.foundryAgents if agent.name == self.AGENT_NAME), None)
        if agentdef is None:
            agentdef = await shared.project_client.agents.create_version(
                agent_name=self.AGENT_NAME,
                definition=PromptAgentDefinition(
                    model="gpt-4.1",
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

MUST return detection_result in json format exactly as received from the tool, NEVER CHANGE STRUCTURE OR ANY CALCULATION. 
Return ONLY valid JSON, no other text or explanation.

Expected structure:
{
  "detection_result": {
    "image_dimensions": [width, height],
    "coordinate_system": "2D with origin at bottom-left, y-axis pointing up",
    "objects": [
      {
        "id": 0,
        "name": "object_name",
        "position_2d": [x, y],
        "center_pixels": [x, y],
        "area_pixels": number,
        "orientation_degrees": number
      }
    ],
    "distances": [
      {
        "from": "object1",
        "to": "object2",
        "distance_pixels": number,
        "distance_units": number,
        "from_position": [x, y],
        "to_position": [x, y]
      }
    ]
  },
  "blob": "url_or_path"
}
'''
                ),
            )
        
        self.agent = ObserverChatAgent(
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
