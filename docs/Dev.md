# Development Guide

## Prerequisites

- **Python 3.8+** for backend services
- **Node.js 18+** for frontend and MCP server
- **Azure OpenAI** account with Realtime API access
- **Azure AI Projects** service
- **Azure Cosmos DB** for data storage
- **Azure Storage** for blob storage
- **LEGO Robot** with BLE capabilities (or use mock mode)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd lego-agent
```

### 2. Environment Setup

Create a `.env` file in the `lego-api/` directory:
```env
AZURE_VOICE_ENDPOINT=your_azure_openai_endpoint
AZURE_VOICE_KEY=your_azure_openai_key
COSMOSDB_ENDPOINT=your_COSMOSDB_ENDPOINT_string
SUSTINEO_STORAGE=your_azure_storage_connection_string
LOCAL_TRACING_ENABLED=false
PROJECT_CONNECTION_STRING=your_azure_ai_projects_connection
DEFAULT_ROBOT_ID=robot_b
```

### 3. Install Dependencies

**Backend (Python):**
```bash
cd lego-api
pip install -r requirements.txt
```

**Robot Agent Package:**
```bash
cd lego-robot-agent
pip install -e .
```

**Frontend (React):**
```bash
cd lego-web
npm install
```

**MCP Server (TypeScript):**
```bash
cd lego-mcp
npm install
npm run build
```

**BLE Service:**
```bash
cd lego-ble
pip install -r requirements.txt
```

**Camera Service:**
```bash
cd lego-cam
pip install -r requirements.txt
```

**Knowledge Base:**
```bash
cd lego-kb
# Configure .env file with Azure credentials
# See lego-kb/README.md for detailed setup instructions
```

**Teams Copilot:**
```bash
cd lego-copilot
npm install
```

## Running the Application

### 1. Start the MCP Server
```bash
cd lego-mcp
npm run build
npm start
```

For testing without a physical robot:
```bash
# MCP has a isMock option for testing
node build/index.js --mock
```

### 2. Start the Main API Server
```bash
cd lego-api
python main.py
```

Or with auto-reload:
```bash
uvicorn main:app --reload --port 8000
```

### 3. Start the BLE Service
```bash
cd lego-ble
python main.py
```

### 4. Start the Camera Service
```bash
cd lego-cam
python server.py
```

### 5. Start the Web Frontend
```bash
cd lego-web
npm run dev
```

Access at: `http://localhost:5173`

### 6. (Optional) Start the Teams Copilot
```bash
cd lego-copilot
npm run dev
# See lego-copilot/README.md for full setup instructions
```

### 7. Run All Services (Alternative)
```bash
# From the root directory
script/run.bat  # Windows
script/run.sh   # Linux/Mac
```

## Development Commands

### Python Services (lego-api)
lego-api uses lego-mcp and lego-robot-agent as dependencies.

```bash
cd lego-api && pip install -r requirements.txt && pip install -e ../lego-robot-agent
uvicorn main:app --reload --port 8000
```

### MCP Server (lego-mcp)
MCP has a isMock option - it will return success without connecting to physical robot. Use this for testing.

```bash
cd lego-mcp && npm install && npm run build
node build/index.js  # Or via MCP client
```

### Web Frontend (lego-web)
```bash
cd lego-web && npm install && npm run dev
```

### Running Tests
```bash
cd lego-robot-agent
python run_tests.py
```

For specific tests:
```bash
python run_tests.py test3  # Object detection test
```

## Project Structure

```
lego-agent/
├── lego-api/          # Main FastAPI backend
│   ├── agent/         # AI agent implementations
│   ├── robot/         # Robot control logic
│   ├── voice/         # Voice processing
│   ├── util/          # Utility functions
│   └── temp/          # Temporary files
├── lego-robot-agent/  # Multi-agent workflow package
│   ├── src/
│   │   ├── lego_robot_agent/
│   │   │   ├── agents/      # Agent implementations
│   │   │   ├── detection/   # Computer vision
│   │   │   └── util/        # Utilities
│   │   └── tests/           # Test scripts
├── lego-mcp/          # Model Context Protocol server
├── lego-web/          # React frontend
├── lego-ble/          # Bluetooth communication
├── lego-cam/          # Camera streaming
├── lego-kb/           # Knowledge base system
│   ├── docs/          # Document storage
│   └── scripts/       # PowerShell management scripts
├── lego-copilot/      # Microsoft Teams bot
├── tests/             # Integration test suites
├── testdata/          # Test images and data
├── script/            # Utility scripts
└── docs/              # Documentation
```

## Configuration

### Agent Configuration
Agents are configured through prompty files in `lego-api/agent/`.

### Voice Settings
Voice interaction parameters in `lego-api/.env`:
- Detection type (semantic_vad, server_vad)
- Eagerness levels (low, medium, high, auto)
- Transcription models
- Voice selection

### Robot Settings
Robot behavior can be configured through:
- MCP server parameters
- Environment variables
- Agent prompty files

## Deployment

### Azure Deployment

Deploy LEGO agents to Azure AI Foundry:
```bash
cd lego-api
python azureagents.py
```

### Teams Copilot Deployment

Deploy Teams bot:
```bash
cd lego-copilot
./scripts/deploy-azure.sh
```

See `lego-copilot/DEPLOYMENT.md` for detailed instructions.

### Docker Deployment

Build and run with Docker:
```bash
# Build image
docker build -t lego-copilot ./lego-copilot

# Run container
docker run -p 3978:3978 --env-file .env.local lego-copilot
```

## Best Practices

### Code Organization
- Keep agent logic in dedicated modules
- Use dependency injection via AgentContext
- Follow existing patterns for new agents

### Testing
- Write unit tests for new features
- Use mock mode for testing without hardware
- Run test suite before committing

### Documentation
- Keep it minimal
- Only essential comments in code
- Update docs/ for significant changes

### Git Workflow
- Create feature branches
- Write descriptive commit messages
- Test thoroughly before pull requests

## Troubleshooting

### MCP Server Issues
```bash
# Rebuild MCP server
cd lego-mcp
npm install
npm run build
```

### Azure Authentication
```bash
# Login to Azure CLI
az login

# Set subscription
az account set --subscription "your-subscription-id"
```

### Python Dependencies
```bash
# Reinstall packages
pip install -r requirements.txt --force-reinstall

# Install robot agent in editable mode
pip install -e ../lego-robot-agent
```

### Port Conflicts
Default ports:
- lego-api: 8000
- lego-web: 5173
- lego-ble: 8001
- lego-cam: 8002
- lego-copilot: 3978

Change ports in respective configuration files if conflicts occur.

## Monitoring

### Local Tracing
Enable in `.env`:
```env
LOCAL_TRACING_ENABLED=true
```

### Azure Monitor
Configure Application Insights for production monitoring.

### Health Checks
- API: `http://localhost:8000/health`
- Copilot: `http://localhost:3978/health`

## API Endpoints

### Health Check
```bash
GET /health
```

### Voice WebSocket
```bash
WS /api/voice/{session_id}
```

### Agent Management
```bash
GET /api/agent/              # List all agents
GET /api/agent/{id}          # Get agent details
POST /api/agent/{id}         # Execute agent
GET /api/agent/refresh       # Refresh agent list
```

### Image Retrieval
```bash
GET /images/{image_id}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Additional Resources

- [Technical Architecture](Technical.md)
- [Testing Guide](Test.md)
- [Solution Overview](Solution.md)
- [Azure AI Projects Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
