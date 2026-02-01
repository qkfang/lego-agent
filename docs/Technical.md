# Technical Architecture

## Overview

The LEGO Agent system is a multi-agent AI system for controlling LEGO robots. The architecture follows a microservices pattern with several interconnected components.

## Architecture Diagram

```
lego-web (React) ←WebSocket→ lego-api (FastAPI) ←MCP→ lego-mcp (Node.js) ←BLE→ lego-ble → Physical Robot
                                    ↓
                           lego-robot-agent (Multi-Agent Workflow)
```

## Core Components

### 1. LEGO API (`lego-api/`)
Main FastAPI backend service providing:
- Real-time voice interaction with Azure OpenAI Realtime API
- Agent orchestration and management
- WebSocket connections for live communication
- Computer vision processing
- Telemetry and monitoring

### 2. LEGO MCP (`lego-mcp/`)
Model Context Protocol server (TypeScript):
- Robot control tool definitions
- Integration with Azure AI Agent Service
- BLE command translation
- Mock mode for testing without physical robots

### 3. LEGO Robot Agent (`lego-robot-agent/`)
Multi-agent workflow system using Microsoft Agent Framework:
- **Orchestrator**: Coordinates overall task execution
- **Observer**: Analyzes field state and objects using computer vision
- **Planner**: Creates action plans based on observations
- **Controller**: Executes robot actions via MCP tools
- **Judger**: Validates task completion

Each agent has `init(context)` and `exec(message)` methods and uses `AgentContext` for dependency injection.

### 4. LEGO Web (`lego-web/`)
React Router v7 frontend application:
- Real-time robot monitoring dashboard
- Voice interaction interface
- Robot control panels
- WebSocket integration for live updates

### 5. LEGO BLE (`lego-ble/`)
Bluetooth communication service:
- Direct BLE communication with LEGO robots
- Protocol handling for robot commands
- FastAPI-based service for robot connectivity

### 6. LEGO Cam (`lego-cam/`)
Camera streaming service:
- Real-time video streaming
- Computer vision processing
- Object detection and tracking capabilities

### 7. LEGO KB (`lego-kb/`)
Knowledge base system:
- Azure AI Search integration for document storage
- Azure Document Intelligence for document parsing
- Support for PDF and Word documents
- PowerShell scripts for index management and ingestion

### 8. LEGO Copilot (`lego-copilot/`)
Microsoft Teams bot integration:
- Chat-based robot control through Teams
- Azure AI Foundry Agent integration
- Per-user conversation threads
- Collaborative robot control

## Key Technical Patterns

### Multi-Agent Workflow
Agents use the Microsoft Agent Framework with `AgentContext` for dependency injection. Sub-agents are located in `lego-robot-agent/src/lego_robot_agent/agents/`.

### MCP Tool Registration
Tools are registered using Zod for validation:
```typescript
mcp.tool("robot_move", "description", { distance_in_cm: z.number() }, async (params) => {...})
```

### Agent Decorator Pattern
Custom agents use the `@agent` decorator in `lego-api/agent/agents.py`.

## Communication Flow

1. **User Interface** (Web/Voice/Teams) → Commands sent via WebSocket/HTTP
2. **LEGO API** → Processes commands, orchestrates agents
3. **Robot Agent** → Multi-agent workflow (Observe → Plan → Execute → Judge)
4. **MCP Server** → Translates agent actions to robot commands
5. **BLE Service** → Sends commands to physical LEGO robot

## AI Integration

### Azure OpenAI Realtime API
- Voice-controlled interactions
- Natural language command processing
- Real-time audio streaming

### Azure AI Foundry
- Agent hosting and management
- Tool orchestration
- Multi-agent coordination

### Computer Vision
- YOLO-based object detection
- Color-based tracking (blue=robot, red=goal, yellow=objects)
- Field analysis and state description

## Monitoring & Observability

- **OpenTelemetry**: Distributed tracing
- **Azure Monitor**: Cloud-based monitoring
- **Real-time Logs**: WebSocket-based log streaming
- **Health Endpoints**: Service status monitoring

## Security

### Authentication
All Azure services use managed identity authentication via `DefaultAzureCredential`:

```python
azure_credential = DefaultAzureCredential()
token_provider = lambda: azure_credential.get_token("https://cognitiveservices.azure.com/.default")
```

### RBAC Configuration
Required Azure roles:
- Cognitive Services User (for voice endpoint)
- Azure AI Developer/Owner (for AI projects)
- Cosmos DB Built-in Data Contributor
- Storage Blob Data Contributor
- Search Service Contributor

## Configuration

### Environment Variables
Key configuration parameters:
- `AZURE_VOICE_ENDPOINT`: Azure OpenAI Realtime API endpoint
- `AZURE_AI_PROJECT_ENDPOINT`: Azure AI Projects connection
- `COSMOSDB_ENDPOINT`: Cosmos DB connection
- `SUSTINEO_STORAGE`: Azure Storage account
- `DEFAULT_ROBOT_ID`: Target robot identifier
- `LOCAL_TRACING_ENABLED`: OpenTelemetry tracing flag

### Agent Configuration
Agents are configured through prompty files and can be customized for specific robot behaviors.

### Voice Settings
- Detection type (semantic_vad, server_vad)
- Eagerness levels (low, medium, high, auto)
- Transcription models
- Voice selection
