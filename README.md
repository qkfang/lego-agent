# LEGO Agent - AI-Powered Robot Control System

A multi-agent AI system for controlling LEGO robots through voice commands, natural language, and real-time interaction. This project combines Azure AI services, computer vision, and multiple interfaces (web, voice, Teams) to create an intelligent robot control platform.

## 🤖 Overview

LEGO Agent enables:
- Voice-controlled robot interactions through Azure OpenAI Realtime API
- Multi-agent orchestration for complex robot behaviors
- Real-time web interface and Microsoft Teams bot
- Computer vision-based object detection and tracking
- Bluetooth Low Energy (BLE) communication with LEGO robots

## 🚀 Quick Start

### Prerequisites
- Python 3.8+, Node.js 18+
- Azure OpenAI account with Realtime API access
- Azure AI Projects service, Cosmos DB, Azure Storage
- LEGO Robot with BLE capabilities (or use mock mode)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd lego-agent

# Install Python dependencies
cd lego-api && pip install -r requirements.txt
cd ../lego-robot-agent && pip install -e .

# Install Node dependencies and build
cd ../lego-mcp && npm install && npm run build
cd ../lego-web && npm install
```

### Configuration
Create `.env` in `lego-api/` directory:
```env
AZURE_VOICE_ENDPOINT=your_azure_openai_endpoint
COSMOSDB_ENDPOINT=your_cosmosdb_endpoint
SUSTINEO_STORAGE=your_azure_storage_url
PROJECT_CONNECTION_STRING=your_azure_ai_projects_connection
DEFAULT_ROBOT_ID=robot_b
```

### Run Services
```bash
# From root directory
script/run.bat  # Windows
script/run.sh   # Linux/Mac
```

Or start individually:
```bash
cd lego-mcp && npm start           # MCP server
cd lego-api && python main.py      # API server
cd lego-web && npm run dev         # Web interface
```

Access web interface at `http://localhost:5173`

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Solution.md](docs/Solution.md)** - Solution overview, features, and use cases
- **[Technical.md](docs/Technical.md)** - Architecture, components, and technical details
- **[Dev.md](docs/Dev.md)** - Development setup, commands, and best practices
- **[Test.md](docs/Test.md)** - Testing guide and troubleshooting

## 🏗️ Architecture

```
lego-web (React) ←WebSocket→ lego-api (FastAPI) ←MCP→ lego-mcp (Node.js) ←BLE→ Physical Robot
                                    ↓
                           lego-robot-agent (Multi-Agent Workflow)
```

### Core Components
- **lego-api**: FastAPI backend with voice, agent orchestration, WebSocket
- **lego-robot-agent**: Multi-agent workflow (Orchestrator, Observer, Planner, Controller, Judger)
- **lego-mcp**: TypeScript MCP server for robot control tools
- **lego-web**: React Router v7 frontend with real-time monitoring
- **lego-ble**: Bluetooth communication service
- **lego-cam**: Camera streaming and computer vision
- **lego-kb**: Knowledge base with Azure AI Search
- **lego-copilot**: Microsoft Teams bot integration

## 🎯 Usage Examples

### Voice Commands
- "Move the robot forward 10 centimeters"
- "Turn left 90 degrees"
- "Open the gripper"
- "Find the red objects on the field"

### API Endpoints
- `GET /health` - Health check
- `WS /api/voice/{session_id}` - Voice WebSocket
- `GET /images/{image_id}` - Image retrieval

### Microsoft Teams
Install LEGO Copilot bot in Teams for collaborative robot control. See `lego-copilot/` for setup.

## 🧪 Testing

```bash
cd lego-robot-agent
python run_tests.py              # Run all tests
python run_tests.py test3 -v     # Specific test with verbose output
```

See [Test.md](docs/Test.md) for detailed testing guide.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Review documentation in `docs/` folder
- Check GitHub issues
- Consult Azure AI documentation for service-specific questions

---

**Note**: Educational and experimental project. Use proper safety measures with physical robots.