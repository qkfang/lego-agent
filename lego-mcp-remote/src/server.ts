import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { initializeServer, setMockMode } from "./config.js";
import { registerRobotTools } from "./robotTools.js";

export function createServer(): McpServer {
  const mcp = new McpServer({
    name: "lego-robot",
    version: "1.0.0",
    description: "MCP server for LEGO ROBOT Service integration",
  });

  // Register all robot commands
  registerRobotTools(mcp);

  return mcp;
}

export async function startServer(): Promise<void> {
  // Check if IS_MOCK environment variable is set
  const isMockEnv = process.env.IS_MOCK === "true";
  if (isMockEnv) {
    setMockMode(true);
    console.error("Running in MOCK mode - robot commands will be simulated");
  }
  
  const serverInitialized = initializeServer();
  
  console.error("\n==================================================");
  console.error(
    `LEGO ROBOT MCP Server ${
      serverInitialized ? "successfully initialized" : "initialization failed"
    }`
  );
  console.error(`Mock Mode: ${isMockEnv ? "ENABLED" : "DISABLED"}`);
  console.error("Starting server...");
  console.error("==================================================\n");

  const mcp = createServer();
  const transport = new StdioServerTransport();
  await mcp.connect(transport);
}
