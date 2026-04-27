import { Command } from "commander";
import { exec } from "child_process";

export const serveCommand = new Command("serve")
  .description("Start the Orca Gateway server")
  .option("-p, --port <port>", "Port", "8000")
  .option("-h, --host <host>", "Host", "0.0.0.0")
  .action(async (opts: any) => {
    console.log(`\n🐋 Starting Orca Gateway on ${opts.host}:${opts.port}\n`);
    const cmd = `python -m uvicorn orca.gateway.app:app --host ${opts.host} --port ${opts.port}`;
    const proc = exec(cmd);
    proc.stdout?.pipe(process.stdout);
    proc.stderr?.pipe(process.stderr);
  });
