# Test Setup Summary

This document summarizes the changes made to enable `test1_action.py` and other test scripts to access Azure resources under the `rg-legobot` resource group.

## Changes Made

### 1. Dependencies Added
Updated `pyproject.toml` to include all required dependencies:
- `mcp` - Model Context Protocol for robot control
- `azure-ai-projects` - Azure AI Foundry project client
- `azure-storage-blob` - Azure Blob Storage client

### 2. Environment Configuration
Created `.env.example` with required Azure configuration variables:
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME` - OpenAI deployment name
- `AZURE_OPENAI_API_VERSION` - API version
- `AZURE_AI_PROJECT_ENDPOINT` - Azure AI Foundry endpoint
- `PROJECT_CONNECTION_STRING` - Project connection string
- `SUSTINEO_STORAGE` - Azure Storage account URL (optional)

### 3. Documentation Updates
- Updated `README.md` with installation and configuration instructions
- Created `AZURE_SETUP.md` with comprehensive Azure authentication guide
- Added testing section with prerequisites and step-by-step instructions

### 4. Cross-Platform Path Resolution
Fixed hardcoded Windows paths in test scripts:
- Created `mcp_test_utils.py` helper module for MCP server path resolution
- Updated all test files (test1_action.py, test4_simple_sequential.py, test5_multiple_agent.py, test6_new_agent.py)
- Path resolution now works on Windows, Linux, and macOS
- Supports `LEGO_MCP_SERVER_PATH` environment variable as fallback

## How to Run Tests

### Prerequisites
1. **Install Azure CLI** (if not already installed)
2. **Authenticate with Azure**:
   ```bash
   az login
   ```
3. **Verify access to resource group**:
   ```bash
   az group show --name rg-legobot
   ```

### Setup Steps

1. **Install dependencies**:
   ```bash
   cd lego-robot-agent
   pip install -e . --pre
   ```

2. **Configure environment** (copy `.env.example` to `.env` and fill in values):
   ```bash
   cp .env.example .env
   # Edit .env with your Azure configuration
   ```

3. **Build MCP server**:
   ```bash
   cd ../lego-mcp
   npm install
   npm run build
   ```

4. **Run test**:
   ```bash
   cd ../lego-robot-agent/src/tests
   python test1_action.py
   ```

## What the Test Does

The `test1_action.py` script:
1. Connects to Azure AI Foundry project to list available agents
2. Initializes MCP (Model Context Protocol) server connection for robot control
3. Creates a LegoControllerAgent with Azure OpenAI integration
4. Executes a simple test command: "hi. 1+1 = ?"

## Expected Behavior

**With Azure authentication:**
- Test connects to Azure OpenAI and AI Foundry
- Initializes MCP connection
- Creates and runs the agent
- Displays agent response

**Without Azure authentication:**
- Test fails with authentication error
- Error message: "Please run 'az login' to setup account"
- Solution: Run `az login` and retry

## Troubleshooting

See `AZURE_SETUP.md` for comprehensive troubleshooting guide covering:
- Authentication issues
- Missing Azure tokens
- Resource access denied
- MCP server connection problems
- Required permissions

## Next Steps

To successfully run the tests with actual Azure resources:

1. **Obtain Azure access**: Contact your Azure administrator for access to `rg-legobot` resource group
2. **Get configuration values**: Use Azure CLI commands in `AZURE_SETUP.md` to retrieve required endpoints and connection strings
3. **Configure .env file**: Fill in all required values in `.env` file
4. **Run tests**: Follow the setup steps above

## Files Modified

- `lego-robot-agent/pyproject.toml` - Added dependencies
- `lego-robot-agent/.env.example` - Created environment template
- `lego-robot-agent/README.md` - Added setup documentation
- `lego-robot-agent/AZURE_SETUP.md` - Created setup guide
- `lego-robot-agent/src/tests/mcp_test_utils.py` - Created path utility
- `lego-robot-agent/src/tests/test1_action.py` - Fixed paths
- `lego-robot-agent/src/tests/test4_simple_sequential.py` - Fixed paths
- `lego-robot-agent/src/tests/test5_multiple_agent.py` - Fixed paths
- `lego-robot-agent/src/tests/test6_new_agent.py` - Fixed paths

## Benefits

These changes provide:
1. **Cross-platform compatibility** - Tests work on Windows, Linux, and macOS
2. **Clear documentation** - Step-by-step guides for setup
3. **Proper dependency management** - All requirements explicitly listed
4. **Flexible configuration** - Environment variables and fallbacks
5. **Better error messages** - Clear guidance when MCP server not found
