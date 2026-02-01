#!/bin/bash
# Quick test runner for lego-web e2e tests
# This script starts services and runs Playwright tests

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== LEGO-WEB E2E Test Runner ===${NC}\n"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ ! -z "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null || true
    fi
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Cleanup complete${NC}"
}

trap cleanup EXIT

# Check if services should be started
if [ "$SKIP_SERVICES" != "true" ]; then
    # 1. Build lego-mcp
    echo -e "${BLUE}[1/4] Building lego-mcp...${NC}"
    cd "$PROJECT_ROOT/lego-mcp"
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run build
    echo -e "${GREEN}✓ lego-mcp built${NC}\n"

    # 2. Start lego-mcp in mock mode
    echo -e "${BLUE}[2/4] Starting lego-mcp in mock mode...${NC}"
    IS_MOCK=true node build/index.js > /tmp/lego-mcp-test.log 2>&1 &
    MCP_PID=$!
    echo -e "${GREEN}✓ lego-mcp started (PID: $MCP_PID)${NC}\n"
    sleep 2

    # 3. Start lego-web dev server
    echo -e "${BLUE}[3/4] Starting lego-web dev server...${NC}"
    cd "$PROJECT_ROOT/lego-web"
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev > /tmp/lego-web-test.log 2>&1 &
    WEB_PID=$!
    echo -e "${GREEN}✓ lego-web started (PID: $WEB_PID)${NC}\n"

    # Wait for web server to be ready
    echo -e "${BLUE}Waiting for web server to be ready...${NC}"
    MAX_RETRIES=60
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Web server is ready!${NC}\n"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 1
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${RED}✗ Web server failed to start${NC}"
        echo -e "${YELLOW}Check logs at /tmp/lego-web-test.log${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Skipping service startup (SKIP_SERVICES=true)${NC}\n"
fi

# 4. Run Playwright tests
echo -e "${BLUE}[4/4] Running Playwright tests...${NC}"
cd "$PROJECT_ROOT"
npx playwright test

echo -e "\n${GREEN}=== Tests Complete ===${NC}"
echo -e "${BLUE}View report with: npx playwright show-report${NC}"
