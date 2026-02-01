#!/bin/bash
# Start services for end-to-end testing with mock mode enabled
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting services for end-to-end testing...${NC}"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${RED}Stopping services...${NC}"
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
    fi
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Cleanup complete${NC}"
}

trap cleanup EXIT

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 1. Build lego-mcp
echo -e "${BLUE}Building lego-mcp...${NC}"
cd "$PROJECT_ROOT/lego-mcp"
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to build lego-mcp${NC}"
    exit 1
fi
echo -e "${GREEN}lego-mcp built successfully${NC}"

# 2. Start lego-mcp in mock mode in the background
echo -e "${BLUE}Starting lego-mcp in mock mode...${NC}"
cd "$PROJECT_ROOT/lego-mcp"
IS_MOCK=true node build/index.js > /tmp/lego-mcp.log 2>&1 &
MCP_PID=$!
echo -e "${GREEN}lego-mcp started (PID: $MCP_PID)${NC}"

# Wait a bit for MCP to start
sleep 2

# 3. Start lego-api in the background
echo -e "${BLUE}Starting lego-api...${NC}"
cd "$PROJECT_ROOT/lego-api"
# Check if requirements are installed
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -e ../lego-robot-agent
else
    source venv/bin/activate
fi

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/lego-api.log 2>&1 &
API_PID=$!
echo -e "${GREEN}lego-api started (PID: $API_PID)${NC}"

# Wait for API to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}Services are ready!${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Services failed to start within timeout${NC}"
    exit 1
fi

# Keep script running and wait for cleanup
echo -e "${GREEN}Services are running. Press Ctrl+C to stop.${NC}"
wait
