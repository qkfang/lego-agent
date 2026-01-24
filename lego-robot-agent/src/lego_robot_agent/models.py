"""
Data models for LEGO Robot Agent.
"""

import datetime
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, List

from .util.paths import find_repo_root


class RobotData:
    """
    Manages robot state and file paths for the agent workflow.
    """
    
    def __init__(self, root: str = ""):
        if not root:
            # repo root -> lego-api/temp
            root = str(find_repo_root(Path(__file__).resolve()) / "lego-api" / "temp")
        self.root = root
        self.runid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.field_data = {}
        self.sequence = 0

    def step0_img_path(self) -> str:
        return str(Path(self.root) / f"{self.runid}_step0_img_path.jpg")

    def step1_analyze_img(self) -> str:
        return str(Path(self.root) / f"{self.runid}_step1_analyze_img.jpg")

    def step1_analyze_json(self) -> str:
        return str(Path(self.root) / f"{self.runid}_step1_analyze_json.json")

    def step1_analyze_json_data(self) -> str:
        with open(self.step1_analyze_json(), "r", encoding="utf-8") as file:
            contents = file.read()
        return contents

    def step2_plan_json(self) -> str:
        return str(Path(self.root) / f"{self.runid}_step2_plan_json.json")

    def step2_plan_json_data(self) -> str:
        with open(self.step2_plan_json(), "r", encoding="utf-8") as file:
            contents = file.read()
        return contents


class RoboProcessArgs:
    """
    Arguments for image processing in object detection.
    """
    
    def __init__(self):
        self.image_path = "image_input.jpg"
        self.method = "color"
        self.templates = None
        self.target_objects = ["blue", "red"]
        self.confidence = 0.5
        self.output = "image_o.json"
        self.visualize = "image_v.json"
        self.pixels_per_unit = 1.0
        self.no_display = False
        self.no_preprocessing = False


@dataclass
class Content:
    """Represents agent return content."""
    type: Literal["text", "image", "video", "tool_calls"]
    content: List[dict]
