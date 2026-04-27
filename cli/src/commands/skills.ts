import { Command } from "commander";
import { OrcaClient } from "../client.js";

export const skillsCommand = new Command("skills")
  .description("Manage skills");

skillsCommand
  .command("list")
  .description("List available skills")
  .option("--gateway <url>", "Gateway URL", "http://localhost:8000")
  .action(async (opts: any) => {
    const client = new OrcaClient(opts.gateway);
    try {
      const data = await client.listSkills();
      console.log(`\n🐋 Available Skills (${data.count})\n`);
      for (const skill of data.skills) {
        console.log(`  • ${skill.name}: ${skill.description}`);
      }
    } catch (err: any) {
      console.error("Error:", err.message);
    }
  });

skillsCommand
  .command("search <query>")
  .description("Search skills")
  .option("--gateway <url>", "Gateway URL", "http://localhost:8000")
  .action(async (query: string, opts: any) => {
    const client = new OrcaClient(opts.gateway);
    const data = await client.searchSkills(query);
    console.log(`Found ${data.count} skills matching "${query}"`);
    for (const skill of data.skills) {
      console.log(`  • ${skill.name}: ${skill.description}`);
    }
  });
