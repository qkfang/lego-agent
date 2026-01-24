"""Utility functions for wrapping MCP tools as callable functions for agent framework."""
import json
from typing import Any, Callable
from agent_framework import ai_function


def create_mcp_tool_wrapper(mcp_tool, session) -> Callable:
    """
    Create a callable wrapper function for an MCP tool.
    
    Args:
        mcp_tool: The MCP tool object with name, description, and inputSchema
        session: The MCP ClientSession to call tools on
        
    Returns:
        A callable async function that invokes the MCP tool
    """
    tool_name = mcp_tool.name
    tool_description = mcp_tool.description or f"MCP tool: {tool_name}"
    input_schema = mcp_tool.inputSchema or {"type": "object", "properties": {}}
    
    # Extract required parameters from schema
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    
    # Build parameter documentation
    param_docs = []
    for param_name, param_info in properties.items():
        param_type = param_info.get("type", "any")
        param_desc = param_info.get("description", "")
        param_docs.append(f"    {param_name} ({param_type}): {param_desc}")
    
    params_docstring = "\n".join(param_docs) if param_docs else "    No parameters"
    
    # Create the wrapper function dynamically
    async def mcp_tool_wrapper(**kwargs) -> str:
        """Wrapper that calls the MCP tool via the session."""
        try:
            result = await session.call_tool(tool_name, kwargs)
            # Handle different result types
            if hasattr(result, 'content'):
                # MCP returns content list with text/image items
                contents = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        contents.append(item.text)
                    elif hasattr(item, 'data'):
                        contents.append(f"[Binary data: {item.mimeType}]")
                return "\n".join(contents) if contents else str(result)
            return str(result)
        except Exception as e:
            return f"Error calling MCP tool {tool_name}: {str(e)}"
    
    # Set function metadata for the agent framework
    mcp_tool_wrapper.__name__ = tool_name
    mcp_tool_wrapper.__doc__ = f"{tool_description}\n\nParameters:\n{params_docstring}"
    
    # Apply the @ai_function decorator to make it compatible with agent framework
    decorated_wrapper = ai_function(description=tool_description)(mcp_tool_wrapper)
    
    return decorated_wrapper


def wrap_mcp_tools(mcp_tools, session) -> list:
    """
    Wrap a list of MCP tools into callable functions for agent framework.
    
    Args:
        mcp_tools: List of MCP tool objects
        session: The MCP ClientSession
        
    Returns:
        List of callable tool functions
    """
    wrapped_tools = []
    for mcp_tool in mcp_tools:
        try:
            wrapped = create_mcp_tool_wrapper(mcp_tool, session)
            wrapped_tools.append(wrapped)
            print(f"Wrapped MCP tool: {mcp_tool.name}")
        except Exception as e:
            print(f"Failed to wrap MCP tool {mcp_tool.name}: {e}")
    return wrapped_tools
