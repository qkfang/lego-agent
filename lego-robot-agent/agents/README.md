# Agent Definitions

This directory contains the Microsoft Agent Framework YAML definitions for all LEGO Robot agents.

## Overview

Each YAML file defines an agent using the Microsoft Agent Framework schema. The agents are loaded at runtime by the agent classes in `src/lego_robot_agent/agents/`.

## Agent Files

- **orchestrator.yaml**: Coordinates the overall multi-agent workflow
- **observer.yaml**: Captures and analyzes the robot field state using camera
- **planner.yaml**: Creates step-by-step action plans for the robot
- **controller.yaml**: Executes physical robot actions via MCP tools
- **judger.yaml**: Evaluates goal completion based on field data

## YAML Format

The YAML files follow the Microsoft Agent Framework schema:

```yaml
kind: prompt                     # Type of agent definition
name: agent-name                 # Machine-readable identifier
displayName: Agent Display Name  # Human-readable name
description: Brief description   # Agent purpose
metadata:
  authors:
    - Author Name
  tags:
    - tag1
    - tag2
model:
  id: gpt-4o                     # Model identifier
  provider: azure-openai         # Model provider
tools:                           # Optional: List of tools
  - tool_name
instructions: |                  # Agent prompt/instructions
  Multi-line agent instructions
  that define the agent's behavior
```

## Modifying Agents

To modify an agent's behavior:

1. Edit the corresponding YAML file
2. Update the `instructions` field with your desired behavior
3. Optionally update the `model.id` to use a different model
4. The changes will be picked up on the next agent initialization

## Benefits

- **Separation of Concerns**: Prompts are separated from code
- **Easy Maintenance**: Update agent behaviors without code changes
- **Version Control**: Track prompt changes independently
- **Reusability**: Share agent definitions across projects
- **Standards Compliance**: Follow Microsoft Agent Framework best practices

## Tools

Some agents use tools to interact with the system:

- **observer.yaml**: Uses `get_field_state_by_camera` to capture field images
- **planner.yaml**: Uses MCP tools to understand available robot actions
- **controller.yaml**: Uses MCP tools to execute robot actions

The tools are registered in the agent classes when the agent is initialized.
