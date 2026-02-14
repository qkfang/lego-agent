// Simple MCP SSE client to test tools list - keeps SSE connection alive
import fetch from 'node-fetch';

const BASE_URL = 'https://termless-marg-hotly.ngrok-free.dev';

async function testMCPServer() {
  console.log('Testing LEGO Robot MCP Server via ngrok...\n');
  
  // 1. Health check
  console.log('1. Health check...');
  const healthRes = await fetch(`${BASE_URL}/health`);
  const health = await healthRes.json();
  console.log('   ✓', health);
  
  // 2. Establish SSE connection and keep it alive
  console.log('\n2. Establishing SSE connection and listening for events...');
  const sseRes = await fetch(`${BASE_URL}/sse`);
  
  let sessionId = null;
  let buffer = '';
  
  // Continuously read SSE stream
  (async () => {
    for await (const chunk of sseRes.body) {
      buffer += chunk.toString();
      
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer
      
      let currentEvent = null;
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.substring(7);
        } else if (line.startsWith('data: ')) {
          const data = line.substring(6);
          
          // Handle endpoint event
          if (currentEvent === 'endpoint' && !sessionId) {
            const match = data.match(/sessionId=([a-f0-9-]+)/);
            if (match) {
              sessionId = match[1];
              console.log(`   ✓ Got sessionId: ${sessionId}`);
              
              // Send tools/list request after getting sessionId
              setTimeout(() => sendToolsRequest(sessionId), 200);
            }
          }
          
          // Handle JSON-RPC responses
          if (data.startsWith('{')) {
            try {
              const json = JSON.parse(data);
              console.log('\n   📨 SSE Response:', JSON.stringify(json, null, 2));
              
              if (json.result && json.result.tools) {
                console.log(`\n✅ SUCCESS! Found ${json.result.tools.length} tools:`);
                json.result.tools.forEach((tool, idx) => {
                  console.log(`   ${idx + 1}. ${tool.name}: ${tool.description}`);
                });
                process.exit(0);
              }
            } catch (e) {
              // Not JSON
            }
          }
        }
      }
    }
  })().catch(err => {
    console.error('SSE stream error:', err);
    process.exit(1);
  });
}

async function sendToolsRequest(sessionId) {
  console.log('\n3. Sending tools/list request...');
  
  const toolsRequest = {
    jsonrpc: '2.0',
    method: 'tools/list',
    id: 1
  };
  
  try {
    const messageRes = await fetch(`${BASE_URL}/message?sessionId=${sessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(toolsRequest)
    });
    
    console.log(`   Status: ${messageRes.status}`);
    
    // For SSE transport, the response comes via SSE stream, not in POST response
    if (messageRes.status !== 202 && messageRes.status !== 200) {
      const text = await messageRes.text();
      console.log('   ⚠️  Response:', text);
    } else {
      console.log('   ⏳ Waiting for response on SSE stream...');
    }
  } catch (error) {
    console.error('   ✗ Request failed:', error.message);
    process.exit(1);
  }
}

testMCPServer().catch(console.error);
