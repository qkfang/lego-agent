"""Utility function to resolve MCP server path for tests."""
import os
import sys
from pathlib import Path


def get_mcp_server_path() -> Path:
    """
    Get the path to the MCP server build file.
    
    Tries the following in order:
    1. LEGO_MCP_SERVER_PATH environment variable
    2. Relative path from repository root
    
    Returns:
        Path to the MCP server index.js file
        
    Raises:
        SystemExit if the MCP server cannot be found
    """
    # Check environment variable first
    env_path = os.environ.get("LEGO_MCP_SERVER_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
    
    # Try to find it relative to this file
    # This file is in lego-robot-agent/src/tests/
    current_dir = Path(__file__).parent  # tests directory
    repo_root = current_dir.parent.parent.parent  # Go up to lego-agent root
    mcp_server_path = repo_root / "lego-mcp" / "build" / "index.js"
    
    if mcp_server_path.exists():
        return mcp_server_path
    
    # If we still can't find it, print an error and exit
    print(f"Error: MCP server not found at {mcp_server_path}")
    print("Please build the MCP server first:")
    print("  cd lego-mcp")
    print("  npm install")
    print("  npm run build")
    print("Or set LEGO_MCP_SERVER_PATH environment variable to the path of index.js")
    sys.exit(1)
