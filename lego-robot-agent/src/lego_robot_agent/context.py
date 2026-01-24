"""
AgentContext - Dependency injection container for LEGO Robot Agent.

Replaces global state (shared.py) with explicit dependency passing.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional, TYPE_CHECKING

from .util.paths import find_repo_root

if TYPE_CHECKING:
    from .models import RobotData


@dataclass
class AgentContext:
    """
    Context container for all dependencies needed by the LEGO agent system.
    
    This replaces the global `shared.py` module with explicit dependency injection,
    making the code more testable and avoiding global state.
    
    Attributes:
        azure_client: The Azure OpenAI chat client for agent creation
        mcp_session: The MCP client session for robot communication
        mcp_tools: Wrapped MCP tools for agent use
        robot_data: Robot state and file path management
        notify_callback: Optional callback for sending notifications
        temp_folder: Path to the temporary folder for file monitoring
        is_test: Whether running in test mode
        test_count: Counter for test mode image selection
    """
    
    # Required dependencies
    azure_client: Any  # AzureOpenAIChatClient
    
    # Optional dependencies (can be set later)
    mcp_session: Optional[Any] = None  # MCP ClientSession
    mcp_tools: Optional[list] = None  # Wrapped MCP tools
    robot_data: Optional["RobotData"] = None
    
    # Callbacks
    notify_callback: Optional[Callable[..., Coroutine[Any, Any, None]]] = None
    
    # Configuration
    temp_folder: str = ""
    is_test: bool = False
    test_count: int = 1
    
    # Runtime state
    workflow: Optional[Any] = None
    last_image: Optional[str] = None
    
    def __post_init__(self):
        """Initialize robot_data if not provided."""
        if self.robot_data is None:
            from .models import RobotData
            self.robot_data = RobotData()
        if not self.temp_folder:
            self.temp_folder = str(
                # repo root -> lego-mcp/temp
                find_repo_root(Path(__file__).resolve()) / "lego-mcp" / "temp"
            )
    
    async def notify(
        self,
        id: str,
        subagent: str,
        status: str,
        information: str = None,
        content: Any = None,
        output: bool = False,
    ) -> None:
        """
        Send a notification through the callback if available.
        
        Args:
            id: Notification identifier
            subagent: Name of the agent sending the notification
            status: Current status message
            information: Optional additional information
            content: Optional content object
            output: Whether this is an output notification
        """
        if self.notify_callback is not None:
            await self.notify_callback(
                id=id,
                subagent=subagent,
                status=status,
                information=information,
                content=content,
                output=output,
            )
    
    def increment_test_count(self) -> int:
        """Increment and return the test count."""
        self.test_count += 1
        return self.test_count
