import { startServer } from "./server.js";

// Start the server
async function main() {
  try {
    await startServer();
  } catch (error) {
    console.error(
      `FATAL: ${error instanceof Error ? error.message : String(error)}`
    );
    process.exit(1);
  }
}

// Start the server unconditionally
main();