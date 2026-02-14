// Simple MCP SSE client to test tools list
import fetch from 'node-fetch';

const BASE_URL = 'https://termless-marg-hotly.ngrok-free.dev';

async function testMCPServer() {
  console.log('Testing LEGO Robot MCP Server via ngrok...\n');
  
  // 1. Health check
  console.log('1. Health check...');
  const healthRes = await fetch(`${BASE_URL}/health`);
  const health = await healthRes.json();
  console.log('   ✓', health);
  
  // 2. Establish SSE connection and KEEP IT OPEN
  console.log('\n2. Establishing SSE connection...');
  const sseRes = await fetch(`${BASE_URL}/sse`);
  
  let sessionId = null;
  
  // Read the first SSE event to get sessionId (but don't close the connection)
  const reader = sseRes.body;
  let buffer = '';
  
  // Create an async iterator that we won't fully consume
  const iterator = reader[Symbol.asyncIterator]();
  
  // Read chunks until we get the sessionId
  while (!sessionId) {
    const { value, done } = await iterator.next();
    if (done) break;
    
    buffer += value.toString();
    
    // Look for the endpoint event with sessionId
    const endpointMatch = buffer.match(/data:\s*(\/message\?sessionId=([a-f0-9-]+))/);
    if (endpointMatch) {
      sessionId = endpointMatch[2];
      console.log('   ✓ Got sessionId:', sessionId);
      // DON'T break the connection - it needs to stay alive
    }
    
    // Once we have sessionId, we can send the message (connection stays open)
    if (sessionId) {
      // Wait a bit for connection to stabilize
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // 3. Send tools/list request (while SSE is still connected)
      console.log('\n3. Requesting tools list...');
      const toolsRequest = {
        jsonrpc: '2.0',
        method: 'tools/list',
        id: 1
      };
      
      const messageRes = await fetch(`${BASE_URL}/message?sessionId=${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(toolsRequest)
      });
      
      console.log('   Status:', messageRes.status);
      
      const responseText = await messageRes.text();
      console.log('   Response text:', responseText);
      
      let result;
      try {
        result = JSON.parse(responseText);
      } catch (e) {
        console.log('\n✗ Failed to parse JSON:', e.message);
        console.log('   Raw response:', responseText.substring(0, 200));
        process.exit(1);
      }
      console.log('\n   Response:');
      console.log(JSON.stringify(result, null, 2));
      
      if (result.result && result.result.tools) {
        console.log(`\n✓ SUCCESS! Found ${result.result.tools.length} tools:`);
        result.result.tools.forEach(tool => {
          console.log(`   - ${tool.name}: ${tool.description}`);
        });
      } else if (result.error) {
        console.log('\n✗ Error:', result.error.message);
      } else {
        console.log('\n✗ Unexpected response format');
      }
      
      // Now we can exit (this will close the SSE connection)
      process.exit(0);
    }
  }
  
  if (!sessionId) {
    console.error('   ✗ Failed to get sessionId');
  }
}

testMCPServer().catch(console.error);
