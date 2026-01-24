# LEGO Agent - AI-Powered Robot Control System

A comprehensive multi-agent system for controlling LEGO robots through AI agents, voice commands, and real-time interaction. This project combines Azure AI services, computer vision, and real-time communication to create an intelligent robot control platform.

## 🤖 Overview

The LEGO Agent system is a sophisticated platform that enables:
- Voice-controlled robot interactions through Azure OpenAI Realtime API
- Computer vision-based object detection and tracking
- Multi-agent orchestration for complex robot behaviors
- Real-time web interface for robot monitoring and control
- Bluetooth Low Energy (BLE) communication with LEGO robots
- Model Context Protocol (MCP) integration for extensible agent capabilities

## 🏗️ Architecture

The system consists of several interconnected components:

### Core Components

1. **LEGO API** (`lego-api/`) - Main FastAPI backend service
   - Real-time voice interaction with Azure OpenAI
   - Agent orchestration and management
   - WebSocket connections for live communication
   - Computer vision processing
   - Telemetry and monitoring

2. **LEGO MCP** (`lego-mcp/`) - Model Context Protocol server
   - TypeScript-based MCP server for robot control
   - Extensible tool definitions for robot actions
   - Integration with Azure AI Agent Service

3. **LEGO Web** (`lego-web/`) - React frontend application
   - Real-time robot monitoring dashboard
   - Voice interaction interface
   - Robot control panels
   - Built with React Router v7 and modern web technologies

4. **LEGO BLE** (`lego-ble/`) - Bluetooth communication service
   - Direct BLE communication with LEGO robots
   - Protocol handling for robot commands
   - FastAPI-based service for robot connectivity

5. **LEGO Cam** (`lego-cam/`) - Camera streaming service
   - Real-time video streaming
   - Computer vision processing
   - Object detection and tracking capabilities

6. **LEGO KB** (`lego-kb/`) - Knowledge base system
   - Azure AI Search integration for document storage
   - Azure Document Intelligence for document parsing
   - Support for PDF and Word documents
   - PowerShell scripts for index management and ingestion

## 🚀 Features

### AI-Powered Interactions
- **Voice Control**: Natural language commands through Azure OpenAI Realtime API
- **Multi-Agent System**: Coordinated robot behaviors through multiple AI agents
- **Computer Vision**: Object detection, tracking, and field analysis
- **Intelligent Planning**: Automated path planning and task execution

### Robot Capabilities
- **Movement Control**: Forward/backward movement and turning
- **Arm Control**: Gripper/arm open/close operations
- **Sound Effects**: Beep commands and audio feedback
- **Sensor Integration**: Real-time sensor data processing

### Real-Time Features
- **Live Video Streaming**: Real-time camera feeds
- **WebSocket Communication**: Instant updates and commands
- **Voice Streaming**: Continuous voice interaction
- **Telemetry**: Real-time monitoring and logging

## 📋 Prerequisites

- **Python 3.8+** for backend services
- **Node.js 18+** for frontend and MCP server
- **Azure OpenAI** account with Realtime API access
- **Azure AI Projects** service
- **Azure Cosmos DB** for data storage
- **Azure Storage** for blob storage
- **LEGO Robot** with BLE capabilities

## 🛠️ Installation

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
COSMOSDB_CONNECTION=your_cosmosdb_connection_string
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

## 🏃‍♂️ Running the Application

### 1. Start the MCP Server
```bash
cd lego-mcp
npm run build
npm start
```

### 2. Start the Main API Server
```bash
cd lego-api
python main.py
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

### 6. Run All Services (Alternative)
```bash
# From the root directory
script/run.bat
```

## 🎯 Usage

### Voice Commands
Connect to the web interface and use natural language commands:
- "Move the robot forward 10 centimeters"
- "Turn left 90 degrees"
- "Open the gripper"
- "Analyze what you see in the camera"
- "Find the red objects on the field"

### Web Interface
- Access the dashboard at `http://localhost:5173`
- Monitor robot status and camera feeds
- Send manual commands through the interface
- View real-time telemetry and logs

### API Endpoints

**Health Check:**
```bash
GET /health
```

**Voice WebSocket:**
```bash
WS /api/voice/{session_id}
```

**Image Retrieval:**
```bash
GET /images/{image_id}
```

## 🧪 Testing

Run the test suite:
```bash
cd lego-api
pytest tests/
```

Available test scenarios:
- Simple sequential agent operations
- Multiple agent coordination
- YOLO object detection
- Action execution validation

## 📁 Project Structure

```
lego-agent/
├── lego-api/          # Main FastAPI backend
│   ├── agent/         # AI agent implementations
│   ├── robot/         # Robot control logic
│   ├── voice/         # Voice processing
│   ├── util/          # Utility functions
│   └── temp/          # Temporary files
├── lego-mcp/          # Model Context Protocol server
├── lego-web/          # React frontend
├── lego-ble/          # Bluetooth communication
├── lego-cam/          # Camera streaming
├── lego-kb/           # Knowledge base system
│   ├── docs/          # Document storage
│   └── scripts/       # PowerShell management scripts
├── tests/             # Test suites
├── testdata/          # Test images and data
└── script/            # Utility scripts
```

## 🔧 Configuration

### Agent Configuration
Agents are configured through prompty files and can be customized for specific robot behaviors.

### Voice Settings
Voice interaction parameters can be adjusted:
- Detection type (semantic_vad, server_vad)
- Eagerness levels (low, medium, high, auto)
- Transcription models
- Voice selection

### Robot Settings
Robot behavior can be configured through the MCP server and environment variables.

## 🔍 Monitoring

The system includes comprehensive monitoring:
- **OpenTelemetry**: Distributed tracing
- **Azure Monitor**: Cloud-based monitoring
- **Real-time Logs**: WebSocket-based log streaming
- **Health Endpoints**: Service status monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the issues section
- Review the test files for usage examples
- Consult the Azure AI documentation for service-specific questions

## 🔮 Future Enhancements

- Enhanced computer vision capabilities
- Additional robot models support
- Mobile app integration
- Cloud deployment templates
- Advanced AI agent behaviors
- Multi-robot coordination

---

**Note**: This project is designed for educational and experimental purposes. Ensure proper safety measures when working with physical robots.