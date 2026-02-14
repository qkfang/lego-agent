import express from "express";
import cors from "cors";
import ngrok from "@ngrok/ngrok";
import { randomUUID } from "crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { initializeServer, setMockMode } from "./config.js";
import { registerRobotTools } from "./robotTools.js";

const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;
const NGROK_AUTHTOKEN = process.env.NGROK_AUTHTOKEN;

export function createServer(): McpServer {
  const mcp = new McpServer({
    name: "lego-robot",
    version: "1.0.0",
  }, {
    capabilities: {}
  });

  // Register all robot commands
  registerRobotTools(mcp);

  return mcp;
}

export async function startNgrokServer(): Promise<void> {
  const isMockEnv = process.env.IS_MOCK === "true";
  if (isMockEnv) {
    setMockMode(true);
    console.error("Running in MOCK mode - robot commands will be simulated");
  }

  const serverInitialized = initializeServer();

  console.error("\n==================================================");
  console.error(`LEGO ROBOT MCP Server with ngrok`);
  console.error(`Mock Mode: ${isMockEnv}`);
  console.error(`Local Port: ${PORT}`);
  console.error("==================================================\n");

  const app = express();
  app.use(cors());

  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({ status: "ok", server: "lego-robot-mcp" });
  });

  // Store server instances by session ID
  const servers: Map<string, { server: McpServer; transport: SSEServerTransport }> = new Map();

  // SSE endpoint - GET request to establish SSE connection
  app.get("/sse", async (req, res) => {
    console.error("New SSE connection request");

    const transport = new SSEServerTransport("/message", res);
    const server = createServer();
    
    // Connect will call transport.start() automatically
    await server.connect(transport);
    
    const sessionId = transport.sessionId;

    // Store server and transport for this session
    servers.set(sessionId, { server, transport });

    // Clean up when connection closes
    req.on("close", () => {
      console.error(`SSE connection closed for session ${sessionId}`);
      servers.delete(sessionId);
    });

    console.error(`MCP server connected via SSE for session ${sessionId}`);
  });

  // Message endpoint - POST request to send messages
  app.post("/message", express.json(), async (req, res) => {
    console.error("POST /message received");

    const sessionId = req.query.sessionId as string | undefined;

    if (!sessionId) {
      res.status(400).json({
        jsonrpc: "2.0",
        error: {
          code: -32000,
          message: "Missing sessionId query parameter"
        },
        id: null
      });
      return;
    }

    const session = servers.get(sessionId);
    if (!session) {
      res.status(404).json({
        jsonrpc: "2.0",
        error: {
          code: -32000,
          message: "Session not found"
        },
        id: null
      });
      return;
    }

    // Pass the parsed body to handlePostMessage
    await session.transport.handlePostMessage(req, res, req.body);
  });

  // Start Express server
  const server = app.listen(PORT, async () => {
    console.error(`HTTP server listening on port ${PORT}`);
    try {
      // Start ngrok tunnel
      const listener = await ngrok.connect({
        addr: PORT,
        authtoken: NGROK_AUTHTOKEN,
      });

      console.error("\n🚀 ngrok tunnel established!");
      console.error("==================================================");
      console.error(`Public URL: ${listener.url()}`);
      console.error(`SSE endpoint: ${listener.url()}/sse`);
      console.error(`Message endpoint: ${listener.url()}/message?sessionId=<session_id>`);
      console.error(`Health check: ${listener.url()}/health`);
      console.error("==================================================");
      console.error("\nMCP HTTP+SSE transport is ready!");
      console.error("Clients should:");
      console.error(`  1. GET ${listener.url()}/sse to establish SSE connection`);
      console.error(`  2. POST to ${listener.url()}/message?sessionId=<session_id> to send messages`);
      console.error("==================================================\n");
    } catch (error) {
      console.error("Failed to start ngrok tunnel:", error);
      if (!NGROK_AUTHTOKEN) {
        console.error("\n⚠️  NGROK_AUTHTOKEN environment variable not set!");
        console.error(
          "Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
        );
        console.error('Set it with: $env:NGROK_AUTHTOKEN="your_token_here"\n');
      }
      process.exit(1);
    }
  });

  // Handle graceful shutdown
  process.on("SIGINT", () => {
    console.error("\nShutting down server...");
    
    // Close all sessions
    for (const [sessionId, session] of servers.entries()) {
      try {
        session.transport.close();
        console.error(`Session ${sessionId} closed`);
      } catch (e) {
        console.error(`Error closing session ${sessionId}:`, e);
      }
    }
    servers.clear();

    server.close(() => {
      console.error("Server closed");
      process.exit(0);
    });
  });
}

// Start the server
async function main() {
  try {
    await startNgrokServer();
  } catch (error) {
    console.error(`FATAL: ${error}`);
    process.exit(1);
  }
}

main();
