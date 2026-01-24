"""
Unit tests for lego-robot-agent package.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

# Add the lego-robot-agent package to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lego_robot_agent.util.paths import find_repo_root

from lego_robot_agent.models import RobotData, RoboProcessArgs, Content
from lego_robot_agent.context import AgentContext


class TestRobotData:
    """Tests for RobotData class."""

    def test_robot_data_initialization(self):
        """Test RobotData initializes with correct defaults."""
        robot_data = RobotData()
        
        expected_root = str(find_repo_root(Path(__file__).resolve()) / "lego-api" / "temp")
        assert robot_data.root == expected_root
        assert robot_data.runid is not None
        assert robot_data.field_data == {}
        assert robot_data.sequence == 0

    def test_robot_data_custom_root(self):
        """Test RobotData with custom root path."""
        custom_root = "/custom/path"
        robot_data = RobotData(root=custom_root)
        
        assert robot_data.root == custom_root

    def test_step_paths_contain_runid(self):
        """Test that step file paths include the run ID."""
        robot_data = RobotData()
        
        assert robot_data.runid in robot_data.step0_img_path()
        assert robot_data.runid in robot_data.step1_analyze_img()
        assert robot_data.runid in robot_data.step1_analyze_json()
        assert robot_data.runid in robot_data.step2_plan_json()

    def test_step_paths_have_correct_extensions(self):
        """Test that step file paths have correct file extensions."""
        robot_data = RobotData()
        
        assert robot_data.step0_img_path().endswith(".jpg")
        assert robot_data.step1_analyze_img().endswith(".jpg")
        assert robot_data.step1_analyze_json().endswith(".json")
        assert robot_data.step2_plan_json().endswith(".json")


class TestRoboProcessArgs:
    """Tests for RoboProcessArgs class."""

    def test_default_initialization(self):
        """Test RoboProcessArgs has correct defaults."""
        args = RoboProcessArgs()
        
        assert args.image_path == "image_input.jpg"
        assert args.method == "color"
        assert args.templates is None
        assert args.target_objects == ["blue", "red"]
        assert args.confidence == 0.5
        assert args.output == "image_o.json"
        assert args.visualize == "image_v.json"
        assert args.pixels_per_unit == 1.0
        assert args.no_display is False
        assert args.no_preprocessing is False


class TestAgentContext:
    """Tests for AgentContext class."""

    def test_context_creation(self):
        """Test AgentContext can be created with mocked dependencies."""
        mock_azure_client = MagicMock()
        mock_mcp_session = MagicMock()
        
        context = AgentContext(
            azure_client=mock_azure_client,
            mcp_session=mock_mcp_session
        )
        
        assert context.azure_client == mock_azure_client
        assert context.mcp_session == mock_mcp_session


class TestLegoAgent:
    """Tests for LegoAgent main orchestrator."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock AgentContext."""
        context = MagicMock(spec=AgentContext)
        context.azure_client = MagicMock()
        context.mcp_session = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_context):
        """Test LegoAgent initializes correctly."""
        from lego_robot_agent.agent import LegoAgent
        
        agent = LegoAgent(mock_context)
        
        assert agent.context == mock_context
        assert agent._init_done is False
        assert agent._action_executing is False
        assert agent._action_ending is False

    @pytest.mark.asyncio
    async def test_agent_init_method(self, mock_context):
        """Test LegoAgent.init() initializes all sub-agents."""
        from lego_robot_agent.agent import LegoAgent
        
        agent = LegoAgent(mock_context)
        
        # Mock all sub-agent init methods
        agent._orchestrator.init = AsyncMock()
        agent._observer.init = AsyncMock()
        agent._planner.init = AsyncMock()
        agent._controller.init = AsyncMock()
        agent._judger.init = AsyncMock()
        
        await agent.init()
        
        assert agent._init_done is True
        agent._orchestrator.init.assert_called_once_with(mock_context)
        agent._observer.init.assert_called_once_with(mock_context)
        agent._planner.init.assert_called_once_with(mock_context)
        agent._controller.init.assert_called_once_with(mock_context)
        agent._judger.init.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_agent_init_idempotent(self, mock_context):
        """Test that calling init() multiple times only initializes once."""
        from lego_robot_agent.agent import LegoAgent
        
        agent = LegoAgent(mock_context)
        
        # Mock all sub-agent init methods
        agent._orchestrator.init = AsyncMock()
        agent._observer.init = AsyncMock()
        agent._planner.init = AsyncMock()
        agent._controller.init = AsyncMock()
        agent._judger.init = AsyncMock()
        
        await agent.init()
        await agent.init()  # Call again
        
        # Should only be called once
        assert agent._orchestrator.init.call_count == 1


class TestSubAgents:
    """Tests for individual sub-agents."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock AgentContext."""
        context = MagicMock(spec=AgentContext)
        context.azure_client = MagicMock()
        context.mcp_session = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_orchestrator_agent_init(self, mock_context):
        """Test LegoOrchestratorAgent initialization."""
        from lego_robot_agent.agents import LegoOrchestratorAgent
        
        agent = LegoOrchestratorAgent()
        await agent.init(mock_context)
        
        assert agent._context == mock_context

    @pytest.mark.asyncio
    async def test_observer_agent_init(self, mock_context):
        """Test LegoObserverAgent initialization."""
        from lego_robot_agent.agents import LegoObserverAgent
        
        agent = LegoObserverAgent()
        await agent.init(mock_context)
        
        assert agent._context == mock_context

    @pytest.mark.asyncio  
    async def test_planner_agent_init(self, mock_context):
        """Test LegoPlannerAgent initialization."""
        from lego_robot_agent.agents import LegoPlannerAgent
        
        agent = LegoPlannerAgent()
        await agent.init(mock_context)
        
        assert agent._context == mock_context

    @pytest.mark.asyncio
    async def test_controller_agent_init(self, mock_context):
        """Test LegoControllerAgent initialization."""
        from lego_robot_agent.agents import LegoControllerAgent
        
        agent = LegoControllerAgent()
        await agent.init(mock_context)
        
        assert agent._context == mock_context

    @pytest.mark.asyncio
    async def test_judger_agent_init(self, mock_context):
        """Test LegoJudgerAgent initialization."""
        from lego_robot_agent.agents import LegoJudgerAgent
        
        agent = LegoJudgerAgent()
        await agent.init(mock_context)
        
        assert agent._context == mock_context
