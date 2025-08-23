export interface Robot {
  robot_name: string;
  robot_id: string;
}

export interface McpResponse {
  [x: string]: unknown;
  content: Array<{
    [x: string]: unknown;
    type: "text";
    text: string;
  }>;
  _meta?: any;
  isError?: boolean;
}

export interface RobotMoveParams {
  robot_id: string;
  distance: number;
}

export interface RobotTurnParams {
  robot_id: string;
  degree: number;
}

export interface RobotBeepParams {
  robot_id: string;
}

export interface RobotArmParams {
  robot_id: string;
  openOrClose: string;
}

export interface RobotActionParams {
  robot_id: string;
  command: string;
}

export interface RobotTalkParams {
  robot_id: string;
  sentence: string;
}

export interface RobotSettingParams {
  mode: string;
}
