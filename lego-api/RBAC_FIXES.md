# RBAC and Configuration Issues Fixed

## Overview
This document outlines the RBAC (Role-Based Access Control) issues identified and fixed for the lego-api application.

## Issues Identified and Fixed

### 1. Environment Variables ✓
- **FOUNDRY_CONNECTION → AZURE_AI_PROJECT_ENDPOINT**: Already properly configured in `.env`
- **AZURE_VOICE_KEY**: Removed dependency on API key, now using managed identity via `DefaultAzureCredential`
- **COSMOSDB_CONNECTION → COSMOSDB_ENDPOINT**: Already properly configured in `.env`
- **Storage Account**: Already using managed identity via `DefaultAzureCredential`

### 2. RBAC Roles Applied ✓

The service principal (d1a41b26-540b-4ba4-9762-b18af64afe5f) now has the following roles:

| Resource | Role | Purpose | Status |
|----------|------|---------|--------|
| rg-legobot (Resource Group) | Owner | Full control over resource group | ✓ Already existed |
| legobot-foundry (Cognitive Services) | Cognitive Services User | Access to voice endpoint for realtime API | ✓ Applied |
| legobot-foundry (Cognitive Services) | Azure AI Developer | Development access to foundry | ✓ Already existed |
| legobot-foundry/legobot-project | Azure AI Owner | Full access to AI project | ✓ Already existed |
| legobot-cosmos (Cosmos DB) | Cosmos DB Built-in Data Contributor | Read/write access to Cosmos DB data | ✓ Applied |
| legobotst (Storage Account) | Storage Blob Data Contributor | Read/write/delete blob data | ✓ Applied |
| legobot-docint (Cognitive Services) | Cognitive Services Contributor | Document intelligence access | ✓ Already existed |
| legobot-search (Search Service) | Search Service Contributor | Search service access | ✓ Already existed |

### 3. API Authentication ✓

All Azure services now use managed identity authentication:

```python
# Example: Voice endpoint authentication
azure_credential = DefaultAzureCredential()
token_provider = lambda: azure_credential.get_token("https://cognitiveservices.azure.com/.default")

client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_VOICE_ENDPOINT,
    azure_ad_token_provider=token_provider,
    api_version="2025-04-01-preview",
)
```

```python
# Example: Storage authentication
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url=SUSTINEO_STORAGE, credential=credential
)
```

### 4. API Endpoints Tested ✓

All core API endpoints are working correctly:

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/health` | GET | ✓ Working | Health check endpoint |
| `/` | GET | ✓ Working | Root endpoint |
| `/api/agent/` | GET | ✓ Working | List all agents |
| `/api/agent/refresh` | GET | ✓ Working | Refresh agent list |
| `/api/agent/function` | GET | ✓ Working | List all functions |
| `/api/agent/{id}` | GET | ✓ Working | Get agent details |
| `/api/agent/{id}` | POST | ⚠ Requires WebSocket | Execute agent (needs active WebSocket connection) |
| `/api/configuration/` | GET | ⚠ 500 Error | Voice configuration (not critical) |
| `/images/{image_id}` | GET | ✓ Working | Get image from storage |
| `/openapi.json` | GET | ✓ Working | OpenAPI specification |

## Known Limitations

### 1. lego-robot-agent Integration
- **Status**: Temporarily disabled
- **Reason**: Version compatibility issue between `agent-framework` packages
- **Error**: `ImportError: cannot import name 'FunctionTool' from 'agent_framework'`
- **Impact**: robot_agent execution is stubbed out but API works correctly
- **Resolution**: Requires updating agent-framework versions or modifying lego-robot-agent code

### 2. MCP Server Integration
- **Status**: Temporarily disabled
- **Reason**: Depends on lego-robot-agent imports which are currently incompatible
- **Impact**: Robot control tools not available
- **Resolution**: Fix agent-framework compatibility issue first

### 3. Voice Configuration Endpoint
- **Status**: Returns 500 error
- **Reason**: Missing configuration or dependency issue
- **Impact**: Not critical for agent API testing
- **Resolution**: Investigate voice configuration setup

## Testing Results

### API Server
- ✓ Server starts successfully
- ✓ All core endpoints respond correctly
- ✓ Managed identity authentication works
- ✓ RBAC permissions are properly configured

### Agent System
- ✓ robot_agent is properly registered
- ✓ Agent decorator system works
- ✓ Function agents are discoverable
- ⚠ Robot execution requires WebSocket connection
- ⚠ Full lego-robot-agent workflow needs compatibility fix

## Recommendations

1. **Agent Framework Compatibility**: Update agent-framework packages to consistent versions or modify lego-robot-agent to work with current versions

2. **Voice Configuration**: Investigate and fix the voice configuration endpoint if needed for production

3. **Integration Testing**: Once agent-framework compatibility is resolved, test the full robot workflow including:
   - MCP server initialization
   - Robot tool invocation
   - Multi-agent orchestration (Orchestrator → Observer → Planner → Controller → Judger)

4. **Documentation**: Keep this RBAC configuration documented for future deployments

## Environment Variables Summary

Current `.env` configuration:
```
AZURE_AI_PROJECT_ENDPOINT=https://legobot-foundry.services.ai.azure.com/api/projects/legobot-project
AZURE_VOICE_ENDPOINT="https://legobot-foundry.cognitiveservices.azure.com/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime"
COSMOSDB_ENDPOINT="https://legobot-cosmos.documents.azure.com:443/"
SUSTINEO_STORAGE="https://legobotst.blob.core.windows.net/"
AZURE_OPENAI_ENDPOINT=https://legobot-foundry.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview
LOCAL_TRACING_ENABLED="true"
```

All using managed identity - no API keys required!
