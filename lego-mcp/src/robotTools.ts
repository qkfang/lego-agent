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
  RobotSettingParams 
} from "./types.js";

export function registerRobotTools(mcp: McpServer): void {
  // Robot Settings
  mcp.tool(
    "robot_setting",
    "Configure robot settings such as running mode. default mode is live, which means the robot will perform actual actions. test mode means the robot will not perform any actions, but will simulate them.",
    {
      mode: z.string().describe("running mode of the robot: test or mock or live."),
    },
    async (param: RobotSettingParams): Promise<McpResponse> => {
      try {
        if (param.mode === "test") {
          setTestMode(true);
          return {
            content: [
              {
                type: "text" as const,
                text: "Robot is set to test mode. No actual robot actions will be performed.",
              },
            ],
          };
        } else if (param.mode === "mock") {
          setMockMode(true);
          return {
            content: [
              {
                type: "text" as const,
                text: "Robot is set to mock mode. No actual robot actions will be performed.",
              },
            ],
          };
        } else {
          setTestMode(false);
          setMockMode(false);
          return {
            content: [
              {
                type: "text" as const,
                text: "Robot is set to live mode. Actual robot actions will be performed.",
              },
            ],
          };
        }
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

  // Robot List
  mcp.tool(
    "robot_list",
    "Get all the available robots",
    {},
    async (): Promise<McpResponse> => {
      try {
        const robots: Robot[] = [
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

  // Robot Move
  mcp.tool(
    "robot_move",
    "Move robot forward or backward. positive value in centimetre means forward, negative value in centimetre means backward. no decimal value is allowed.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      distance: z.number().describe("distance in centimetre that the robot should move")
    },
    async (param: RobotMoveParams): Promise<McpResponse> => {
      try {
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
        return {
          content: [{ type: "text" as const, text: `${param.robot_id} robot moved ${param.distance}cm` }],
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

  // Robot Turn
  mcp.tool(
    "robot_turn",
    "Turn robot left or right. positive value in degrees means right, negative value in degrees means left.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      degree: z.number().describe("degree that the robot should turn")
    },
    async (param: RobotTurnParams): Promise<McpResponse> => {
      try {
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
        return {
          content: [{ type: "text" as const, text: `${param.robot_id} robot turned ${param.degree} degrees` }],
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

  // Robot Beep
  mcp.tool(
    "robot_beep",
    "Make robot beep and make a sound.",
    {
      robot_id: z.string().describe("robot_id that should perform the action")
    },
    async (param: RobotBeepParams): Promise<McpResponse> => {
      try {
        let code = '';
        if (!isTest) {
          code = `
    await sound.beep(880, 200, 100)
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

  // Robot Arm
  mcp.tool(
    "robot_arm",
    "Make robot arm open or close.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      openOrClose: z.string().describe("openOrClose, 1=open, 0=close")
    },
    async (param: RobotArmParams): Promise<McpResponse> => {
      try {
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
        return {
          content: [{ type: "text" as const, text: `${param.robot_id} robot arm ${param.openOrClose === "1" ? "opened" : "closed"}` }],
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

  // Robot Action
  mcp.tool(
    "robot_action",
    "Make robot do an action that is not movement.",
    {
      robot_id: z.string().describe("robot_id that should perform the action"),
      command: z.string().describe("command name that the robot should perform")
    },
    async (param: RobotActionParams): Promise<McpResponse> => {
      try {
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
        return {
          content: [{ type: "text" as const, text: `${param.robot_id} robot executed: ${param.command}` }],
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
}
