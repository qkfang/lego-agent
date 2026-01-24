# LEGO Robot Agent

A standalone Python package for multi-agent orchestration of LEGO robot control.

## Overview

This package provides the `LegoAgent` class and supporting agents for controlling LEGO robots through a multi-agent workflow:

- **Orchestrator Agent**: Coordinates the overall workflow
- **Observer Agent**: Captures and analyzes the robot field state
- **Planner Agent**: Creates step-by-step action plans
- **Controller Agent**: Executes physical robot actions via MCP tools
- **Judger Agent**: Evaluates goal completion

## Installation

```bash
# Install from local path (development mode)
pip install -e ../lego-robot-agent --pre

# Or with YOLO support for object detection
pip install -e ../lego-robot-agent[yolo] --pre
```

## Configuration

### Azure Authentication

This package requires Azure authentication to access Azure OpenAI and Azure AI Foundry services. Before running tests or using the package, authenticate with Azure CLI:

```bash
az login
```

Make sure you have access to the required Azure resource group (e.g., `rg-legobot`).

### Environment Variables

Create a `.env` file in the project root or set the following environment variables:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure AI Foundry Project Configuration
AZURE_AI_PROJECT_ENDPOINT=your-project-endpoint
PROJECT_CONNECTION_STRING=your-connection-string

# Azure Storage Configuration (optional)
SUSTINEO_STORAGE=your-storage-account-url
```

You can copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

## Usage

```python
from lego_robot_agent import LegoAgent, AgentContext
from lego_robot_agent.models import RobotData

# Create context with your Azure OpenAI client and MCP session
context = AgentContext(
    azure_client=your_azure_client,
    mcp_session=your_mcp_session,
    mcp_tools=your_mcp_tools,
    robot_data=RobotData(),
)

# Create and initialize the agent
agent = LegoAgent(context)
await agent.init()

# Run the agent with a goal
await agent.run("Pick up the coke and deliver it to Bowser")
```

## Architecture

The package uses dependency injection instead of global state:

- `AgentContext`: Holds all runtime dependencies (Azure client, MCP session, etc.)
- Each sub-agent receives the context during initialization
- Event callbacks for notifications are passed through the context

## Project Structure

```
lego-robot-agent/
├── src/
│   └── lego_robot_agent/
│       ├── __init__.py
│       ├── agent.py              # Main LegoAgent class
│       ├── context.py            # AgentContext for dependency injection
│       ├── models.py             # RobotData and related models
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── orchestrator.py
│       │   ├── observer.py
│       │   ├── planner.py
│       │   ├── controller.py
│       │   └── judger.py
│       └── detection/
│           ├── __init__.py
│           ├── detector.py
│           └── tracker.py
├── pyproject.toml
└── README.md
```

## Running Tests

Before running tests:

1. **Authenticate with Azure**:
   ```bash
   az login
   ```

2. **Set up environment variables** (copy `.env.example` to `.env` and configure)

3. **Start the MCP server** (required for robot control tests):
   ```bash
   cd ../../lego-mcp
   npm install
   npm run build
   npm start
   ```

4. **Run tests**:
   ```bash
   cd src/tests
   python test1_action.py
   ```

### Available Tests

- `test1_action.py` - Test robot controller agent with MCP tools
- `test4_simple_sequential.py` - Simple sequential agent operations
- `test5_multiple_agent.py` - Multiple agent coordination
- `test_lego_robot_agent.py` - Full LEGO robot agent workflow
