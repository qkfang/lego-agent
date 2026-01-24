"""
Compatibility wrapper for lego-robot-agent package.

This module re-exports the LegoAgent and related classes from the 
standalone lego-robot-agent package, maintaining backward compatibility
with existing code while using the refactored module structure.

Usage (new style):
    from lego_robot_agent import LegoAgent, AgentContext
    
Usage (legacy, via this wrapper):
    from robot.lego_agent import LegoAgent, create_context_from_shared

"""

# Import from the new standalone package
try:
    from lego_robot_agent import LegoAgent, AgentContext, RobotData, Content
    from lego_robot_agent.agents import (
        LegoOrchestratorAgent,
        LegoObserverAgent,
        LegoPlannerAgent,
        LegoControllerAgent,
        LegoJudgerAgent,
    )
    from lego_robot_agent.detection import ObjectDetector, create_sample_color_ranges, run_detection
    
    USING_NEW_PACKAGE = True
except ImportError:
    # Fallback to local imports if new package not installed
    from robot.robot_agent import LegoAgent
    from robot.robot_agent_orchestrator import LegoOrchestratorAgent
    from robot.robot_agent_observer import LegoObserverAgent
    from robot.robot_agent_planner import LegoPlannerAgent
    from robot.robot_agent_controller import LegoControllerAgent
    from robot.robot_agent_judger import LegoJudgerAgent
    from robot.robotmodel import RobotData
    from robot.object_detector import ObjectDetector, create_sample_color_ranges, run as run_detection
    from model import Content
    
    # Dummy AgentContext for compatibility
    class AgentContext:
        def __init__(self, **kwargs):
            raise NotImplementedError(
                "AgentContext requires the lego-robot-agent package. "
                "Install with: pip install -e ../lego-robot-agent"
            )
    
    USING_NEW_PACKAGE = False


def create_context_from_shared():
    """
    Create an AgentContext from the current shared module state.
    
    This is a helper function to bridge the old shared.py globals
    with the new dependency injection pattern.
    
    Returns:
        AgentContext: A context initialized from shared module state
    """
    import lego_robot_agent.shared as shared
    
    return AgentContext(
        azure_client=shared.azure_client,
        mcp_session=shared.mcprobot,
        mcp_tools=shared.robotmcptools,
        robot_data=shared.robotData,
        notify_callback=shared.notify,
        is_test=shared.isTest,
        test_count=shared.isTestCount,
    )


__all__ = [
    "LegoAgent",
    "AgentContext",
    "RobotData",
    "Content",
    "LegoOrchestratorAgent",
    "LegoObserverAgent",
    "LegoPlannerAgent",
    "LegoControllerAgent",
    "LegoJudgerAgent",
    "ObjectDetector",
    "create_sample_color_ranges",
    "run_detection",
    "create_context_from_shared",
    "USING_NEW_PACKAGE",
]
