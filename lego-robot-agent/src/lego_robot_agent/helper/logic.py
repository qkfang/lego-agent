import json
import requests
from agent_framework import ai_function
from ..context import AgentContext
from ..type.models import FieldData


_observer_context: "AgentContext" = None


async def _process_image(context: "AgentContext") -> FieldData:
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
    args.pixels_per_unit = 10
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

    # Validate and structure the data using Pydantic model
    field_data = FieldData(detection_result=detection_result, blob=blob)
    robot_data.field_data = field_data.model_dump()
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
        url = "http://192.168.0.186:5000/photo"
        response = requests.get(url)
        img_data = response.content

    with open(context.robot_data.step0_img_path(), "wb") as f:
        f.write(img_data)

    field_data = await _process_image(context)
    # Return JSON string using Pydantic's model_dump_json for proper serialization
    return field_data.model_dump_json(indent=2)
