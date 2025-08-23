import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { runble, isTest, setTestMode, setMockMode } from "./config.js";
import type { 
  Robot, 
  McpResponse, 
  RobotMoveParams, 
  RobotTurnParams, 
  RobotBeepParams, 
  RobotArmParams, 
  RobotActionParams, 
  RobotTalkParams, 
  RobotSettingParams 
} from "./types.js";

// Reusable error handling utility
function createErrorResponse(error: unknown): McpResponse {
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

// Reusable success response utility
function createSuccessResponse(message: string): McpResponse {
  return {
    content: [
      {
        type: "text" as const,
        text: message,
      },
    ],
  };
}

// Wrapper function for safe execution with error handling
async function safeExecute<T>(
  operation: () => Promise<T> | T,
  successMessage: string | ((result: T) => string)
): Promise<McpResponse> {
  try {
    const result = await operation();
    const message = typeof successMessage === 'function' 
      ? successMessage(result) 
      : successMessage;
    return createSuccessResponse(message);
  } catch (error) {
    return createErrorResponse(error);
  }
}

export function registerRobotTools(mcp: McpServer): void {
  // Robot Settings
  mcp.tool(
    "robot_setting",
    "Configure robot settings such as running mode. default mode is live, which means the robot will perform actual actions. test mode means the robot will not perform any actions, but will simulate them.",
    {
      mode: z.string().describe("running mode of the robot: test or mock or live."),
    },
    async (param: RobotSettingParams): Promise<McpResponse> => {
      return safeExecute(
        () => {
          if (param.mode === "test") {
            setTestMode(true);
            return "Robot is set to test mode. No actual robot actions will be performed.";
          } else if (param.mode === "mock") {
            setMockMode(true);
            return "Robot is set to mock mode. No actual robot actions will be performed.";
          } else {
            setTestMode(false);
            setMockMode(false);
            return "Robot is set to live mode. Actual robot actions will be performed.";
          }
        },
        (result) => result
      );
    }
  );

  // Robot List
  mcp.tool(
    "robot_list",
    "Get all the available robots",
    {},
    async (): Promise<McpResponse> => {
      return safeExecute(
        () => {
          const robots: Robot[] = [
            { robot_name: "Agent K", robot_id: "Robot_K" },
            // { robot_name: "robot b", robot_id: "robot_b" }
          ];
          return robots.map(r => `${r.robot_name} (ID: ${r.robot_id})`).join('\n');
        },
        (result) => result
      );
    }
  );

  // Robot Move
  mcp.tool(
    "robot_move",
    "Move robot forward or backward. positive value in centimetre means forward, negative value in centimetre means backward. no decimal value is allowed.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      distance: z.number().describe("distance in centimetre that the robot should move")
    },
    async (param: RobotMoveParams): Promise<McpResponse> => {
      return safeExecute(
        async () => {
          let code = '';
          if (!isTest) {
            code = `
    await move(${param.distance}, Speed.Slow)
    print("done")
    sys.exit(0)
`;
          } else {
            code = `
    await light_matrix.write("mv")
    print("done")
    sys.exit(0)
`;
          }
          await runble(code);
          return `${param.robot_id} robot moved ${param.distance}cm`;
        },
        (result) => result
      );
    }
  );

  // Robot Turn
  mcp.tool(
    "robot_turn",
    "Turn robot left or right. positive value in degrees means right, negative value in degrees means left.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      degree: z.number().describe("degree that the robot should turn")
    },
    async (param: RobotTurnParams): Promise<McpResponse> => {
      return safeExecute(
        async () => {
          let code = '';
          if (!isTest) {
            code = `
    await turn(${param.degree}, Speed.Slow)
    print("done")
    sys.exit(0)
`;
          } else {
            code = `
    await light_matrix.write("tr")
    print("done")
    sys.exit(0)
`;
          }
          await runble(code);
          return `${param.robot_id} robot turned ${param.degree} degrees`;
        },
        (result) => result
      );
    }
  );

  // Robot Beep
  mcp.tool(
    "robot_beep",
    "Make robot beep and make a sound.",
    {
      robot_id: z.string().describe("robot_id that should perform the action")
    },
    async (param: RobotBeepParams): Promise<McpResponse> => {
      return safeExecute(
        async () => {
          let code = '';
          if (!isTest) {
            code = `
    buzz()
    print("done")
    sys.exit(0)
`;
          } else {
            code = `
    await light_matrix.write("bp")
    print("done")
    sys.exit(0)
`;
          }
          await runble(code);
          return `${param.robot_id} robot beeped`;
        },
        (result) => result
      );
    }
  );

  // Robot Arm
  mcp.tool(
    "robot_arm",
    "Make robot arm open or close.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      openOrClose: z.string().describe("openOrClose, 1=open, 0=close")
    },
    async (param: RobotArmParams): Promise<McpResponse> => {
      return safeExecute(
        async () => {
          const openClose = param.openOrClose === "1" ? -100 : 100;
          let code = '';
          if (!isTest) {
            code = `
    await rotateTop(${openClose}, Speed.Slow)
    print("done")
    sys.exit(0)
`;
          } else {
            code = `
    await light_matrix.write("rt")
    print("done")
    sys.exit(0)
`;
          }
          await runble(code);
          return `${param.robot_id} robot arm ${param.openOrClose === "1" ? "opened" : "closed"}`;
        },
        (result) => result
      );
    }
  );
  
  // Robot Action
  mcp.tool(
    "robot_action",
    "Make robot do an action that is not movement.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      command: z.string().describe("command name that the robot should perform")
    },
    async (param: RobotActionParams): Promise<McpResponse> => {
      return safeExecute(
        async () => {
          let code = '';
          if (!isTest) {
            code = `
    ${param.command}
    print("done")
    sys.exit(0)
`;
          } else {
            code = `
    await light_matrix.write("act")
    print("done")
    sys.exit(0)
`;
          }
          await runble(code);
          return `${param.robot_id} robot executed: ${param.command}`;
        },
        (result) => result
      );
    }
  );

  // Robot Talk
  mcp.tool(
    "robot_talk",
    "Make robot talk by displaying a text on screen",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      sentence: z.string().describe("sentence that the robot would like to say or display or express")
    },
    async (param: RobotTalkParams): Promise<McpResponse> => {
      return safeExecute(
        async () => {
          let code = '';
          if (!isTest) {
            code = `
    await light_matrix.write(${param.sentence})
    print("done")
    sys.exit(0)
`;
          } else {
            code = `
    await light_matrix.write("com")
    print("done")
    sys.exit(0)
`;
          }
          await runble(code);
          return `${param.robot_id} robot executed: ${param.sentence}`;
        },
        (result) => result
      );
    }
  );
}
