import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as dotenv from "dotenv";
import { AIProjectsClient } from "@azure/ai-projects";
import type { MessageRole, MessageContentOutput } from "@azure/ai-projects";
import fetch = require("node-fetch");
import * as fs from "fs";
import * as path from "path";

dotenv.config();

var basePythonScript = "";
var isTest = false;

function initializeServer(): boolean {
  const robotFunctionPath = path.resolve("D:/gh-repo/lego-agent/lego-mcp/typescript/src/robot-function.py");
  basePythonScript = fs.readFileSync(robotFunctionPath, "utf8");
  return true;
}

const serverInitialized = initializeServer();
const mcp = new McpServer({
  name: "lego-robot",
  version: "1.0.0",
  description: "MCP server for LEGO ROBOT Service integration",
});



async function run(scriptname: string): Promise<void> {
  
  const { exec } = await import("child_process");
  const { promisify } = await import("util");
  const execAsync = promisify(exec);

  const scriptPath = "ampy --port COM6 run c:/Temp/code.py";
  const { stdout, stderr } = await execAsync(scriptPath);

  // console.log("Script output:", stdout);
}


async function runble(code: string): Promise<void> {
  const fs = await import("fs/promises");
  const path = await import("path");
  const timestamp = Date.now();
  const filename = `script_${timestamp}.py`;
  const filepath = path.join("D:/gh-repo/lego-agent/lego-mcp/temp", filename);
  
  var script = basePythonScript.replace("###placeholder###", code);
  await fs.writeFile(filepath, script, "utf8");

  const response = await fetch("http://127.0.0.1:8001/exec", {
    method: "POST",
    headers: { "Content-Type": "text/plain" },
    body: script
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
}


// async function runble(code: string): Promise<void> {

//   const fs = await import("fs/promises");
//   const path = await import("path");
//   const timestamp = Date.now();
//   const filename = `script_${timestamp}.py`;
//   const filepath = path.join("D:/gh-repo/lego-agent/lego-ble/temp", filename);
//   // console.log('filepath= ' + filepath);

  
//   var script = basePythonScript.replace("###placeholder###", code);
//   await fs.writeFile(filepath, script, "utf8");

//   const scriptCmd = `python D:/gh-repo/lego-agent/lego-ble/python/app.py --program ${filepath}`;

//   // console.log('runble= ' + scriptCmd);
//   // const { stdout, stderr } = await execAsync(scriptCmd);

//   // console.log("Script output:", stdout);
//   // console.log("Script error:", stderr);

//   // Send script to local HTTP server
//   const response = await fetch("http://127.0.0.1:8001/exec", {
//     method: "POST",
//     headers: { "Content-Type": "text/plain" },
//     body: script
//   });
//   // console.log('response.status= ' + response.status);
//   if (!response.ok) {
//     throw new Error(`HTTP error! status: ${response.status}`);
//   }
//   // Optionally, handle response if needed
// }


mcp.tool(
  "robot_list",
  "Get all the vailable robots",
  {
  },
  async () => {
   
    try {
      const robots = [
        { robot_name: "robot k", robot_id: "robot_k" },
        // { robot_name: "robot b", robot_id: "robot_b" }
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
  "robot_move",
  "Move robot forward or backward. positive value in mm means forward, negative value in mm means backward.",
  {
    robot_id: z.string().describe("robot_id that should perform the action"),
    distance: z.number().describe("distance in cm that the robot should move")
  },
  async (param) => {
   
    try {
      var code = '';
      if (!isTest) {
        code =
`
    await move(${param.distance}, Speed.Slow)
    print("done")
    sys.exit(0)
`
      }
      else {
        code =
`
    await light_matrix.write("mv")
    print("done")
    sys.exit(0)
`
      };
      await runble(code);
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
  "robot_turn",
  "Turn robot left or right. positive value in mm means right, negative value in mm means left.",
  {
    robot_id: z.string().describe("robot_id that should perform the action"),
    degree: z.number().describe("degree that the robot should turn")
  },
  async (param) => {
   
    try {
      var code = '';
      if (!isTest) {
        code =
`
    await turn(${param.degree}, Speed.Slow)
    print("done")
    sys.exit(0)
`
      }
      else {
        code =
`
    await light_matrix.write("tr")
    print("done")
    sys.exit(0)
`
      };
      await runble(code);
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
  "robot_beep",
  "Make robot beep and make a sound.",
  {
    robot_id: z.string().describe("robot_id that should perform the action")
  },
  async (param) => {
   
    try {
      var code = '';
      if (!isTest) {
        code =
`
    await sound.beep(880, 200, 100)
    print("done")
    sys.exit(0)
`
      }
      else {
        code =
`
    await light_matrix.write("bp")
    print("done")
    sys.exit(0)
`
      };
      await runble(code);
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


mcp.tool(
  "robot_arm",
  "Make robot arm open or close.",
  {
    robot_id: z.string().describe("robot_id that should perform the action"),
    openOrClose: z.string().describe("openOrClose, 1=open, 0=close")
  },
  async (param) => {
   
    try {
      var openClose = param.openOrClose === "1" ? -100 : 100;
      var code = '';
      if (!isTest) {
        code =
`
    await rotateTop(${openClose}, Speed.Slow)
    print("done")
    sys.exit(0)
`
      }
      else {
        code =
`
    await light_matrix.write("rt")
    print("done")
    sys.exit(0)
`
      };
      await runble(code);
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


mcp.tool(
  "robot_action",
  "Make robot do an action that is not movement .",
  {
    robot_id: z.string().describe("robot_id that should perform the action"),
    command: z.string().describe("command name that the robot should perform")
  },
  async (param) => {
   
    try {
      var code = '';
      if (!isTest) {
        code =
`
    ${param.command}
    print("done")
    sys.exit(0)
`
      }
      else {
        code =
`
    await light_matrix.write("act")
    print("done")
    sys.exit(0)
`
      };
      await runble(code);
      return {
        content: [{ type: "text" as const, text: `${param.robot_id} robot: ${param.command}` }],
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