import { Command } from "commander";
import { OrcaClient } from "../client.js";

export const researchCommand = new Command("research")
  .description("Execute a research workflow")
  .argument("<query>", "Research query")
  .option("-w, --workflow <type>", "Workflow type", "deep_research")
  .option("-d, --depth <n>", "Research depth", "2")
  .option("-s, --sources <n>", "Max sources", "10")
  .option("--gateway <url>", "Gateway URL", "http://localhost:8000")
  .action(async (query: string, opts: any) => {
    const client = new OrcaClient(opts.gateway);
    console.log(`\n🐋 Orca Research: ${query}`);
    console.log(`   Workflow: ${opts.workflow} | Depth: ${opts.depth}\n`);

    try {
      const session = await client.runResearch(
        opts.workflow, query, parseInt(opts.depth), parseInt(opts.sources)
      );
      console.log(`Session: ${session.session_id} (${session.status})`);

      if (session.status === "running") {
        console.log("Polling for results...");
        let result = await client.getSession(session.session_id);
        while (result.status === "running") {
          await new Promise(r => setTimeout(r, 2000));
          result = await client.getSession(session.session_id);
          process.stdout.write(".");
        }
        console.log("\n");
        if (result.result?.summary) {
          console.log(result.result.summary);
        }
      }
    } catch (err: any) {
      console.error("Error:", err.message);
    }
  });
