# LEGO Agent - Solution Overview

## What is LEGO Agent?

LEGO Agent is a comprehensive multi-agent AI system for controlling LEGO robots through natural language commands, voice interaction, and real-time computer vision. The platform combines Azure AI services, computer vision, and real-time communication to create an intelligent robot control platform.

## Key Features

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

### Microsoft Teams Integration
- **Teams Copilot**: Chat-based robot control through Microsoft Teams
- **Collaborative Control**: Team members can interact with robots together
- **Foundry Agent Integration**: Leverages Azure AI Foundry for intelligent responses
- **Easy Deployment**: Simple setup with provided scripts and documentation

## Use Cases

### Educational Applications
- Teaching robotics and AI concepts
- Demonstrating multi-agent systems
- Learning computer vision fundamentals
- Understanding voice AI integration

### Research & Development
- Testing multi-agent coordination algorithms
- Developing new robot behaviors
- Experimenting with computer vision techniques
- Prototyping AI-controlled robotics

### Team Collaboration
- Shared robot control via Teams
- Remote robot operation
- Collaborative task execution
- Educational demos and presentations

## How It Works

### 1. Voice Commands
Connect to the web interface and use natural language:
- "Move the robot forward 10 centimeters"
- "Turn left 90 degrees"
- "Open the gripper"
- "Analyze what you see in the camera"
- "Find the red objects on the field"

### 2. Web Interface
- Access the dashboard at `http://localhost:5173`
- Monitor robot status and camera feeds
- Send manual commands through the interface
- View real-time telemetry and logs

### 3. Microsoft Teams Copilot
- Install the LEGO Copilot bot in Microsoft Teams
- Chat with the bot using natural language commands
- Control robots collaboratively with your team
- Examples: "What can the robot do?", "Move forward 20cm", "Show robot status"

### 4. API Integration
Programmatic access via REST API:
- Health Check: `GET /health`
- Voice WebSocket: `WS /api/voice/{session_id}`
- Image Retrieval: `GET /images/{image_id}`

## Multi-Agent Workflow

The system uses a sophisticated multi-agent workflow:

1. **Orchestrator**: Receives high-level commands and coordinates the workflow
2. **Observer**: Analyzes the current field state using computer vision
3. **Planner**: Creates action plans based on observations and goals
4. **Controller**: Executes robot actions via MCP tools
5. **Judger**: Validates task completion and success

Example workflow for "grab the coke":
1. Observer analyzes field → "Robot at (0,0), red coke at (50cm, 0)"
2. Planner creates plan → "Move forward 50cm, close gripper"
3. Controller executes → Sends move and arm commands
4. Judger validates → "Task completed successfully"

## Computer Vision Capabilities

### Object Detection
- Color-based detection (HSV color space)
- Configurable color ranges for different objects
- Real-time tracking and position estimation

### Field Analysis
- Robot position detection (blue objects)
- Goal detection (red objects)
- Target object detection (yellow objects)
- Spatial relationship analysis

### YOLO Integration
- Advanced object detection
- Multiple object classification
- Improved accuracy for complex scenes

## Azure AI Integration

### Services Used
- **Azure OpenAI**: Voice interaction and natural language processing
- **Azure AI Foundry**: Agent hosting and orchestration
- **Azure Cosmos DB**: Data storage and state management
- **Azure Storage**: Image and blob storage
- **Azure AI Search**: Knowledge base search
- **Azure Document Intelligence**: Document parsing

### Benefits
- Scalable cloud infrastructure
- Enterprise-grade security
- Managed identity authentication
- Integrated monitoring and observability

## Deployment Options

### Local Development
Run all services locally for development and testing:
```bash
script/run.bat  # Windows
script/run.sh   # Linux/Mac
```

### Cloud Deployment
- Azure App Service for API and web frontend
- Azure Container Instances for BLE and camera services
- Azure Bot Service for Teams integration
- Bicep templates for infrastructure as code

### Hybrid Deployment
- Cloud-hosted API and agents
- Local BLE service for robot communication
- Cloud web interface with local robot control

## Future Enhancements

Planned features and improvements:
- Enhanced computer vision capabilities
- Additional robot models support
- Mobile app integration
- Cloud deployment templates
- Advanced AI agent behaviors
- Multi-robot coordination
- ✅ **Microsoft Teams integration** (completed)

## Getting Started

1. **Prerequisites**: Python 3.8+, Node.js 18+, Azure account
2. **Clone Repository**: `git clone <repository-url>`
3. **Configure Azure Services**: Set up required Azure resources
4. **Install Dependencies**: Follow installation guide
5. **Run Services**: Start all components
6. **Test**: Send voice commands or use web interface

For detailed instructions, see [Dev.md](Dev.md).

## Support

For support and questions:
- Check the documentation in the `docs/` folder
- Review test files for usage examples
- Consult the Azure AI documentation for service-specific questions
- Open issues on GitHub for bugs or feature requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This project is designed for educational and experimental purposes. Ensure proper safety measures when working with physical robots.
