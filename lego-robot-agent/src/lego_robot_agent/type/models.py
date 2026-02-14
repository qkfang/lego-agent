from pydantic import BaseModel


class ObjectInfo(BaseModel):
    """Information about a detected object."""
    id: int
    name: str
    position_2d: list[int]
    center_pixels: list[int]
    area_pixels: float
    orientation_degrees: float


class DistanceInfo(BaseModel):
    """Distance information between two objects."""
    from_: str  # using from_ since 'from' is a Python keyword
    to: str
    distance_pixels: float
    distance_units: float
    from_position: list[int]
    to_position: list[int]

    class Config:
        # Map 'from_' field to 'from' in JSON
        fields = {'from_': 'from'}


class DetectionResult(BaseModel):
    """Result of field detection analysis."""
    image_dimensions: list[int]
    coordinate_system: str
    objects: list[ObjectInfo]
    distances: list[DistanceInfo]


class FieldData(BaseModel):
    """Complete field data including detection results and image blob."""
    detection_result: DetectionResult
    blob: str | None = None


class JudgementResult(BaseModel):
    """Result from the judge agent indicating completion status."""
    status: str  # "goal completed" or "goal failed"
    reason: str
    completed: bool


class PlanStep(BaseModel):
    """A single step in the robot action plan."""
    action: str
    args: dict[str, str | int | float]
    explain: str


class RobotPlan(BaseModel):
    """Complete robot action plan with multiple steps."""
    steps: list[PlanStep]


class JudgementResult:
    """Result from the judge agent indicating completion status."""
    completed: bool
    reason: str = ""