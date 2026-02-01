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
pip install -e ../lego-robot-agent

# Or with YOLO support for object detection
pip install -e ../lego-robot-agent[yolo]
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

### Declarative Agent Definitions

Agent prompts and configurations are defined using **Microsoft Agent Framework Declarative YAML** files, located in the `agents/` directory. Each agent has a corresponding YAML file that follows the declarative agent schema:

- **orchestrator.yaml**: Coordinates the overall workflow
- **observer.yaml**: Captures and analyzes the robot field state
- **planner.yaml**: Creates step-by-step action plans
- **controller.yaml**: Executes physical robot actions via MCP tools
- **judger.yaml**: Evaluates goal completion

The YAML files follow the Microsoft Agent Framework declarative schema:

```yaml
kind: Prompt
name: lego-orchestrator
displayName: LEGO Orchestrator Agent
description: Coordinates the overall workflow and decides when the task is complete
instructions: |
  [Agent instructions here]
model:
  id: =Env.AZURE_OPENAI_DEPLOYMENT_NAME
  connection:
    kind: remote
    endpoint: =Env.AZURE_AI_PROJECT_ENDPOINT
```

The agents are created using `AgentFactory` from `agent-framework-declarative`:

```python
from agent_framework.declarative import AgentFactory
from pathlib import Path

# Create agent from YAML file
agent_factory = AgentFactory(client_kwargs={"credential": credential})
agent = agent_factory.create_agent_from_yaml_path(Path("agents/orchestrator.yaml"))
```

This declarative approach provides:
- **Cross-Platform Compatibility**: Same YAML works in Python and .NET
- **Separation of Concerns**: Agent behavior defined separately from code
- **PowerFx Support**: Use environment variables with `=Env.VARIABLE_NAME` syntax
- **Reusability**: Share agent definitions across projects
- **Maintainability**: Update prompts without code changes

## Project Structure

```
lego-robot-agent/
├── agents/                    # Declarative agent YAML definitions
│   ├── orchestrator.yaml
│   ├── observer.yaml
│   ├── planner.yaml
│   ├── controller.yaml
│   ├── judger.yaml
│   └── README.md
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
│       ├── util/
│       │   └── ...
│       └── detection/
│           ├── __init__.py
│           ├── detector.py
│           └── tracker.py
├── pyproject.toml
└── README.md
```
