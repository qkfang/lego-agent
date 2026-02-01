"""
Utility module for loading agent definitions from YAML files.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


def get_agents_dir() -> Path:
    """Get the path to the agents YAML directory."""
    # Get the directory where this file is located
    module_dir = Path(__file__).parent
    # Go up to lego-robot-agent root and find agents directory
    agents_dir = module_dir.parent.parent / "agents"
    return agents_dir


def load_agent_yaml(agent_name: str) -> Dict[str, Any]:
    """
    Load an agent definition from a YAML file.
    
    Args:
        agent_name: Name of the agent (e.g., 'orchestrator', 'observer')
        
    Returns:
        Dictionary containing the agent definition
        
    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is invalid
    """
    agents_dir = get_agents_dir()
    yaml_path = agents_dir / f"{agent_name}.yaml"
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Agent YAML file not found: {yaml_path}")
    
    with open(yaml_path, 'r') as f:
        agent_def = yaml.safe_load(f)
    
    return agent_def


def get_agent_instructions(agent_name: str) -> str:
    """
    Get the instructions/prompt for an agent from its YAML definition.
    
    Args:
        agent_name: Name of the agent (e.g., 'orchestrator', 'observer')
        
    Returns:
        The instructions string for the agent
    """
    agent_def = load_agent_yaml(agent_name)
    return agent_def.get('instructions', '')


def get_agent_model(agent_name: str) -> str:
    """
    Get the model ID for an agent from its YAML definition.
    
    Args:
        agent_name: Name of the agent (e.g., 'orchestrator', 'observer')
        
    Returns:
        The model ID string (e.g., 'gpt-4o')
    """
    agent_def = load_agent_yaml(agent_name)
    model = agent_def.get('model', {})
    return model.get('id', 'gpt-4o')


def get_agent_metadata(agent_name: str) -> Dict[str, Any]:
    """
    Get the complete agent definition metadata from YAML.
    
    Args:
        agent_name: Name of the agent (e.g., 'orchestrator', 'observer')
        
    Returns:
        Dictionary with all agent metadata including name, description, etc.
    """
    agent_def = load_agent_yaml(agent_name)
    return {
        'name': agent_def.get('name'),
        'displayName': agent_def.get('displayName'),
        'description': agent_def.get('description'),
        'model': agent_def.get('model', {}),
        'tools': agent_def.get('tools', []),
        'metadata': agent_def.get('metadata', {})
    }
