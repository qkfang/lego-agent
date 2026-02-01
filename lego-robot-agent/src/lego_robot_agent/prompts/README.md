# Declarative Agent Definitions

This directory contains the **Microsoft Agent Framework Declarative YAML** definitions for all LEGO Robot agents.

## Overview

Each YAML file defines an agent using the Microsoft Agent Framework declarative schema. The agents are created at runtime using `AgentFactory` from the `agent-framework-declarative` package.

## Agent Files

- **orchestrator.yaml**: Coordinates the overall multi-agent workflow
- **observer.yaml**: Captures and analyzes the robot field state using camera
- **planner.yaml**: Creates step-by-step action plans for the robot
- **controller.yaml**: Executes physical robot actions via MCP tools
- **judger.yaml**: Evaluates goal completion based on field data

## Declarative YAML Format

The YAML files follow the [Microsoft Agent Framework Declarative schema](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/declarative):

```yaml
kind: Prompt                     # Type: Prompt for chat-based agents
name: agent-name                 # Machine-readable identifier
displayName: Agent Display Name  # Human-readable name
description: Brief description   # Agent purpose
instructions: |                  # Multi-line agent instructions
  Agent behavior and instructions
  that define how the agent operates
model:
  id: =Env.AZURE_OPENAI_DEPLOYMENT_NAME  # Model with PowerFx env variable
  connection:
    kind: remote                 # Connection type (remote for Azure)
    endpoint: =Env.AZURE_AI_PROJECT_ENDPOINT  # Azure AI endpoint
```

## Key Features

### PowerFx Environment Variables

The YAML files use PowerFx expressions (prefixed with `=`) to access environment variables:

- `=Env.AZURE_OPENAI_DEPLOYMENT_NAME` - Gets the deployment name from environment
- `=Env.AZURE_AI_PROJECT_ENDPOINT` - Gets the Azure AI project endpoint

This allows dynamic configuration without hardcoding values.

### Cross-Platform Compatibility

These YAML definitions work with both:
- **Python**: Using `agent-framework-declarative` package
- **.NET**: Using the same declarative framework

The same YAML file can be used across platforms.

## Usage in Code

Agents are created using `AgentFactory`:

```python
from pathlib import Path
from agent_framework.declarative import AgentFactory
from azure.identity import DefaultAzureCredential

# Create agent from YAML file
agents_dir = Path("agents")
yaml_path = agents_dir / "orchestrator.yaml"

agent_factory = AgentFactory(
    client_kwargs={"credential": DefaultAzureCredential()}
)
agent = agent_factory.create_agent_from_yaml_path(yaml_path)

# Run the agent
response = await agent.run("Your message here")
```

### With Custom Tools (Observer Agent)

The observer agent uses custom Python function tools:

```python
from agent_framework import ai_function

@ai_function(description="Get field state")
async def get_field_state_by_camera() -> str:
    # Implementation here
    pass

# Bind custom tools to the agent
agent_factory = AgentFactory(
    client_kwargs={"credential": credential},
    bindings={"get_field_state_by_camera": get_field_state_by_camera}
)
agent = agent_factory.create_agent_from_yaml_path(yaml_path)
```

## Modifying Agents

To modify an agent's behavior:

1. Edit the corresponding YAML file
2. Update the `instructions` field with your desired behavior
3. Optionally update the `model.id` using PowerFx (e.g., `=Env.CUSTOM_MODEL`)
4. Changes take effect on next agent initialization

## Environment Variables Required

Set these environment variables (via `.env` file or system):

- `AZURE_OPENAI_DEPLOYMENT_NAME` - The Azure OpenAI model deployment name (e.g., "gpt-4o")
- `AZURE_AI_PROJECT_ENDPOINT` - Your Azure AI project endpoint URL

## Benefits

- **Separation of Concerns**: Prompts are separated from code
- **Cross-Platform**: Same YAML works in Python and .NET
- **PowerFx Support**: Dynamic configuration using environment variables
- **Easy Maintenance**: Update agent behaviors without code changes
- **Version Control**: Track prompt changes independently
- **Reusability**: Share agent definitions across projects
- **Standards Compliance**: Follow Microsoft Agent Framework best practices

## Learn More

- [Microsoft Agent Framework Declarative Package](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/declarative)
- [Agent Samples](https://github.com/microsoft/agent-framework/tree/main/agent-samples)
- [PowerFx in YAML](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/declarative#using-powerfx-formulas-in-yaml)
