#!/usr/bin/env node
/**
 * Orca CLI — TypeScript CLI entry point.
 * Delegates to compiled JavaScript from cli/dist/.
 */
const { spawn } = require("child_process");
const path = require("path");

const distPath = path.join(__dirname, "..", "dist", "index.js");

try {
  require(distPath);
} catch (e) {
  console.error("Orca CLI not built. Run: cd cli && npm install && npm run build");
  process.exit(1);
}
