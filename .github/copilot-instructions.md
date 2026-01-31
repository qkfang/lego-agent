# LEGO Agent - AI Coding Instructions

## Architecture Overview

This is a **multi-agent AI system** for controlling LEGO robots. The architecture follows a microservices pattern:

```
lego-web (React) ←WebSocket→ lego-api (FastAPI) ←MCP→ lego-mcp (Node.js) ←BLE→ lego-ble → Physical Robot
                                    ↓
                           lego-robot-agent (Multi-Agent Workflow)
```

### Core Components
- **lego-api/**: Main FastAPI backend - voice interaction, agent orchestration, WebSocket server
- **lego-robot-agent/**: Python package for multi-agent workflow (Orchestrator → Observer → Planner → Controller → Judger)
- **lego-mcp/**: TypeScript MCP server exposing robot tools (`robot_move`, `robot_turn`, `robot_arm`, etc.)
- **lego-web/**: React Router v7 frontend with real-time monitoring
- **lego-ble/**: BLE communication bridge to physical LEGO robots

## Key Patterns

### Multi-Agent Workflow (lego-robot-agent)
Agents use **Microsoft Agent Framework** with `AgentContext` for dependency injection:

Sub-agents in `lego-robot-agent/src/lego_robot_agent/agents/` - each has `init(context)` and `exec(message)` methods.

### MCP Tool Registration (lego-mcp)
Tools are registered using `zod` for validation:
```typescript
mcp.tool("robot_move", "description", { distance_in_cm: z.number() }, async (params) => {...})
```

### Agent Decorator Pattern (lego-api)
Custom agents use the `@agent` decorator in `lego-api/agent/agents.py`:


## Development Commands

### Python Services (lego-api)
lego-api uses lego-mcp and lego-robot-agent as dependencies.

```bash
cd lego-api && pip install -r requirements.txt && pip install -e ../lego-robot-agent
uvicorn main:app --reload --port 8000
```

### MCP Server (lego-mcp)
MCP has a isMock option, it will just return success without connecting to physical robot. use this option for testing.

```bash
cd lego-mcp && npm install && npm run build
node build/index.js  # Or via MCP client
```

### Web Frontend (lego-web)
```bash
cd lego-web && npm install && npm run dev
```

### Rule
Don't need to update documentation, keep it minimal or none.
Minimize comments in code, only essential ones.
Minimize output during thinking step, only very key steps are needed.