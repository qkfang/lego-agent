"""
LEGO Robot Agent sub-agents package.
"""

# Color constants for console output
YELLOW = "\033[33m"
RESET = "\033[0m"

from .orchestrator import LegoOrchestratorAgent
from .observer import LegoObserverAgent
from .planner import LegoPlannerAgent
from .controller import LegoControllerAgent
from .judge import LegoJudgeAgent

__all__ = [
    "LegoOrchestratorAgent",
    "LegoObserverAgent",
    "LegoPlannerAgent",
    "LegoControllerAgent",
    "LegoJudgeAgent",
    "YELLOW",
    "RESET",
]
