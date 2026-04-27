import { Command } from "commander";
import { OrcaClient } from "../client.js";

export const chatCommand = new Command("chat")
  .description("Chat with Orca")
  .argument("<query>", "Your question")
  .option("--gateway <url>", "Gateway URL", "http://localhost:8000")
  .action(async (query: string, opts: any) => {
    console.log(`\n🐋 Orca Chat: ${query}\n`);
    console.log("Chat requires a running Gateway. Start with: orca serve");
  });
