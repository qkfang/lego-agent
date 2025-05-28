#!/usr/bin/env node
/**
 * Azure AI Agent MCP Server
 *
 * This MCP server integrates with Azure AI Foundry to enable connections to
 * Azure AI Agents, utilizing models and knowledge tools available within Azure AI Foundry.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as dotenv from "dotenv";
import { AIProjectsClient } from "@azure/ai-projects";
import type { MessageRole, MessageContentOutput } from "@azure/ai-projects";

// Load environment variables
dotenv.config();

// Global client instance
let aiClient: AIProjectsClient | null = null;

/**
 * Type guard to check if a content item is text content
 */
function isTextContent(
  content: MessageContentOutput
): content is MessageContentOutput & { type: "text"; text: { value: string } } {
  return content.type === "text" && !!(content as any).text?.value;
}

/**
 * Initialize the LEGO ROBOT client
 */
function initializeServer(): boolean {

  return true;
}

// Initialize server
const serverInitialized = initializeServer();

// Create MCP server
const mcp = new McpServer({
  name: "lego-robot",
  version: "1.0.0",
  description: "MCP server for LEGO ROBOT Service integration",
});

async function run(scriptname: string): Promise<void> {
  
  const { exec } = await import("child_process");
  const { promisify } = await import("util");
  const execAsync = promisify(exec);

  const scriptPath = "C:\\Temp\\run.bat";
  const { stdout, stderr } = await execAsync(`"${scriptPath}"`);

  console.log("Script output:", stdout);

}


mcp.tool(
  "list",
  "Get all the vailable robots",
  {
  },
  async () => {
   
    try {
      const robots = [
        { robot_name: "robot k", robot_id: "robot_k" },
        { robot_name: "robot b", robot_id: "robot_b" }
      ];
      return {
        content: [{
          type: "text" as const,
          text: robots.map(r => `${r.robot_name} (ID: ${r.robot_id})`).join('\n')
        }]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: `Error running command: ${
              error instanceof Error ? error.message : String(error)
            }`,
          },
        ],
      };
    }
  }
);

mcp.tool(
  "move",
  "Move robot forward or backward. positive value in mm means forward, negative value in mm means backward.",
  {
    robot_id: z.string().describe("robot_id that should perform the action"),
    distance: z.number().describe("distance in cm that the robot should move")
  },
  async (param) => {
   
    try {
      
      return {
        content: [{ type: "text" as const, text: `${param.robot_id} robot turned ${param.distance}` }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: `Error running command: ${
              error instanceof Error ? error.message : String(error)
            }`,
          },
        ],
      };
    }
  }
);

mcp.tool(
  "turn",
  "Turn robot left or right. positive value in mm means right, negative value in mm means left.",
  {
    robot_id: z.string().describe("robot_id that should perform the action"),
    degree: z.number().describe("degree that the robot should turn")
  },
  async (param) => {
   
    try {
     
      return {
        content: [{ type: "text" as const, text: `${param.robot_id} robot turned ${param.degree}` }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: `Error running command: ${
              error instanceof Error ? error.message : String(error)
            }`,
          },
        ],
      };
    }
  }
);

mcp.tool(
  "beep",
  "Make robot beep and make a sound.",
  {
    robot_id: z.string().describe("robot_id that should perform the action")
  },
  async (param) => {
   
    try {
      await run("");
      return {
        content: [{ type: "text" as const, text: `${param.robot_id} robot beeped` }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: `Error running command: ${
              error instanceof Error ? error.message : String(error)
            }`,
          },
        ],
      };
    }
  }
);

// Main function
async function main() {
  console.error("\n==================================================");
  console.error(
    `LEGO ROBOT MCP Server ${
      serverInitialized ? "successfully initialized" : "initialization failed"
    }`
  );
  console.error("Starting server...");
  console.error("==================================================\n");

  const transport = new StdioServerTransport();
  await mcp.connect(transport);
}
// Start the server unconditionally
main().catch((error) => {
  console.error(
    `FATAL: ${error instanceof Error ? error.message : String(error)}`
  );
  process.exit(1);
});