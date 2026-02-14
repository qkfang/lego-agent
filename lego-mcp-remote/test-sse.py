import requests
import json
import re
import threading
import time

# Test the ngrok MCP server with SSE
BASE_URL = "https://termless-marg-hotly.ngrok-free.dev"

print("Testing LEGO Robot MCP Server via ngrok...")
print(f"Base URL: {BASE_URL}\n")

# 1. Test health endpoint
print("1. Testing health endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# 2. Establish SSE connection and get sessionId
print("2. Establishing SSE connection...")

# Start SSE connection in a separate thread to avoid blocking
session_id = None
sse_response = None

def read_sse():
    global session_id, sse_response
    sse_response = requests.get(f"{BASE_URL}/sse", stream=True)
    print(f"   Status: {sse_response.status_code}")
    
    event_type = None
    for line in sse_response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            print(f"   SSE: {decoded}")
            
            # Track event type
            if decoded.startswith('event: '):
                event_type = decoded[7:]  # Remove 'event: ' prefix
            
            # Look for endpoint event with sessionId
            if decoded.startswith('data: '):
                data_str = decoded[6:]  # Remove 'data: ' prefix
                
                if event_type == 'endpoint':
                    # Extract sessionId from data string (format: /message?sessionId=xxx)
                    match = re.search(r'sessionId=([a-f0-9-]+)', data_str)
                    if match:
                        session_id = match.group(1)
                        print(f"\n   ✓ Got sessionId: {session_id}")
                        return  # Exit after getting sessionId

sse_thread = threading.Thread(target=read_sse, daemon=True)
sse_thread.start()

# Wait for sessionId (max 5 seconds)
for i in range(50):
    if session_id:
        break
    time.sleep(0.1)

if not session_id:
    print("   ✗ Failed to get sessionId")
    exit(1)

# 3. Send tools/list request
print(f"\n3. Requesting tools list...")
tools_request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
}

response = requests.post(
    f"{BASE_URL}/message",
    params={"sessionId": session_id},
    json=tools_request,
    headers={"Content-Type": "application/json"}
)

print(f"   Status: {response.status_code}")
print(f"   Response:\n")
result = response.json()
print(json.dumps(result, indent=2))

if "result" in result and "tools" in result["result"]:
    print(f"\n✓ SUCCESS! Found {len(result['result']['tools'])} tools:")
    for tool in result["result"]["tools"]:
        print(f"   - {tool['name']}: {tool['description']}")
else:
    print("\n✗ Unexpected response format")
