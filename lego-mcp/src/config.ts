import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import * as dotenv from "dotenv";
import fetch from "node-fetch";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export let basePythonScript = "";
export let basePythonScriptTest = "";
export let isTest = false;
export let isMock = false;

export function setTestMode(value: boolean): void {
  isTest = value;
}

export function setMockMode(value: boolean): void {
  isMock = value;
}

export function initializeServer(): boolean {
  try {
    const robotFunctionPath = path.resolve(__dirname, "scripts/robot-function.py");
    const robotFunctionPathTest = path.resolve(__dirname, "scripts/robot-function-test.py");
    basePythonScript = fs.readFileSync(robotFunctionPath, "utf8");
    basePythonScriptTest = fs.readFileSync(robotFunctionPathTest, "utf8");
    return true;
  } catch (error) {
    console.error("Failed to initialize server:", error);
    return false;
  }
}

export async function runble(code: string): Promise<void> {
  if (isMock) {
    return;
  }

  const fs = await import("fs/promises");
  const path = await import("path");
  const timestamp = Date.now();
  const filename = `script_${timestamp}.py`;
  const filepath = path.join(__dirname, "../temp", filename); // lego-mcp/temp
  
  let script = basePythonScript.replace("###placeholder###", code);
  if (isTest) {
    script = basePythonScriptTest.replace("###placeholder###", code); 
  }
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
