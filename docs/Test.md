# Testing Guide

## Quick Start

### Run All Tests
```bash
cd lego-robot-agent
python run_tests.py
```

### Run Specific Test
```bash
python run_tests.py test3                    # Run test3_object_detection.py
python run_tests.py object_detection         # Same as above
python run_tests.py simple_sequential        # Run test4_simple_sequential.py
```

### List Available Tests
```bash
python run_tests.py -l
```

### Verbose Output
```bash
python run_tests.py -v                       # Show all output
python run_tests.py test3 -v                 # Verbose for specific test
```

## Test Scripts

### ✅ test3_object_detection.py - Standalone Unit Test

**Status:** Fully functional, no external dependencies required

**What it tests:**
- Color range configuration for object detection
- Detection of blue (robot), red (coke), and yellow (bowser) objects
- Image loading and preprocessing

**How to run:**
```bash
cd lego-robot-agent
python run_tests.py test3
```

**Direct execution:**
```bash
cd lego-robot-agent/src/tests
python test3_object_detection.py
```

### ⚠️ test1_action.py - Controller Agent Test

**Status:** Requires Azure credentials and MCP server

**What it tests:**
- LegoControllerAgent initialization and execution
- Basic query handling ("hi. 1+1 = ?")
- MCP tool integration

**Prerequisites:**
1. Azure OpenAI endpoint configured in `.env`
2. Azure AI Projects connection
3. MCP server built and accessible
4. Valid Azure credentials (via Azure CLI or environment)

**How to run:**
```bash
# 1. Configure environment
cd lego-robot-agent
cp .env.example .env
# Edit .env with your Azure credentials

# 2. Ensure MCP server is built
cd ../lego-mcp
npm install
npm run build

# 3. Run test
cd ../lego-robot-agent
python run_tests.py test1
```

### ⚠️ test2_yolo.py - Observer Agent Test

**Status:** Requires Azure credentials (MCP optional)

**What it tests:**
- LegoObserverAgent initialization and execution
- Field state description ("describe the current field. blue object is robot, red object is goal.")
- Image capture and analysis

**Prerequisites:**
1. Azure OpenAI endpoint configured
2. Azure AI Projects connection
3. Valid Azure credentials

**How to run:**
```bash
cd lego-robot-agent
python run_tests.py test2
```

### ⚠️ test4_simple_sequential.py - Multi-Agent Sequential Workflow

**Status:** Requires Azure credentials and MCP server

**What it tests:**
- Three-step sequential agent workflow:
  1. **Observer**: Analyze field state
  2. **Planner**: Create action plan ("move robot forward to the coke, and grab it")
  3. **Controller**: Execute planned actions
- Agent coordination and data passing
- MCP tool integration for robot control

**Prerequisites:**
1. Azure OpenAI endpoint configured
2. Azure AI Projects connection
3. MCP server built and running
4. Valid Azure credentials

**How to run:**
```bash
cd lego-robot-agent
python run_tests.py test4
```

### ⚠️ test5_multiple_agent.py - Complete Multi-Agent System

**Status:** Requires Azure credentials and MCP server

**What it tests:**
- Full LegoAgent orchestration
- Complex task: "grab bowser a coke and go back"
- All agents working together (Orchestrator, Observer, Planner, Controller, Judger)
- End-to-end workflow execution

**Prerequisites:**
1. Azure OpenAI endpoint configured
2. Azure AI Projects connection
3. MCP server built and running
4. Valid Azure credentials

**How to run:**
```bash
cd lego-robot-agent
python run_tests.py test5
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd lego-robot-agent
pip install -e .
```

### 2. Build MCP Server

```bash
cd ../lego-mcp
npm install
npm run build
```

### 3. Configure Environment

Create a `.env` file in `lego-robot-agent/`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure AI Projects
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
```

### 4. Authenticate with Azure

```bash
# Login to Azure CLI
az login

# Set your subscription
az account set --subscription "your-subscription-id"
```

## Test Runner Features

### Basic Usage

```bash
python run_tests.py [options] [test_name]
```

### Options

- `-v, --verbose`: Show detailed output for all tests
- `-t, --timeout SECONDS`: Set timeout for each test (default: 30)
- `-l, --list`: List all available tests

### Examples

```bash
# Run all tests with 60 second timeout
python run_tests.py -t 60

# Run specific test with verbose output
python run_tests.py test3 -v

# List all available tests
python run_tests.py -l
```

### Output Format

The test runner provides:
- ✓ Green checkmark for passed tests
- ✗ Red X for failed tests
- Color-coded status messages
- Detailed error output for failed tests
- Test summary with pass/fail counts

## Troubleshooting

### "Module not found" errors

**Solution:** Install the package in editable mode:
```bash
cd lego-robot-agent
pip install -e .
```

### "Cannot find module '/path/to/lego-mcp/build/index.js'"

**Solution:** Build the MCP server:
```bash
cd lego-mcp
npm install
npm run build
```

### "DefaultAzureCredential failed to retrieve a token"

**Solutions:**
1. Login to Azure CLI: `az login`
2. Set environment variable: `export AZURE_TENANT_ID=your-tenant-id`
3. Use managed identity if running on Azure
4. Check that your account has proper permissions

### Tests timeout

**Solution:** Increase timeout with `-t` option:
```bash
python run_tests.py -t 60  # 60 second timeout
```

### "Connection closed" or "Connection refused"

**Possible causes:**
1. MCP server not built
2. Azure credentials not configured
3. Network connectivity issues
4. Azure service temporarily unavailable

**Solutions:**
1. Verify MCP server is built: `ls -la lego-mcp/build/index.js`
2. Check `.env` configuration
3. Verify Azure CLI login: `az account show`
4. Check Azure service health

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Python dependencies
        run: |
          cd lego-robot-agent
          pip install -e .
      
      - name: Build MCP server
        run: |
          cd lego-mcp
          npm install
          npm run build
      
      - name: Run unit tests
        run: |
          cd lego-robot-agent
          python run_tests.py test3
      
      # Optional: Run integration tests with Azure credentials
      - name: Run integration tests
        if: ${{ secrets.AZURE_CREDENTIALS }}
        env:
          AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          AZURE_OPENAI_DEPLOYMENT_NAME: ${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
          AZURE_AI_PROJECT_ENDPOINT: ${{ secrets.AZURE_AI_PROJECT_ENDPOINT }}
        run: |
          cd lego-robot-agent
          python run_tests.py
```

## API Testing

Run the API test suite:
```bash
cd lego-api
pytest tests/
```

Available test scenarios:
- Simple sequential agent operations
- Multiple agent coordination
- YOLO object detection
- Action execution validation

## Test Results

For detailed test results and findings, see the test output from the test runner. The test suite validates:
- Object detection and color-based tracking
- Individual agent capabilities (Observer, Planner, Controller)
- Sequential multi-step workflows
- Complete orchestrated agent interactions
