/**
 * Orca CLI — TypeScript interface to Orca Gateway
 */
import { Command } from "commander";
import { researchCommand } from "./commands/research.js";
import { chatCommand } from "./commands/chat.js";
import { skillsCommand } from "./commands/skills.js";
import { serveCommand } from "./commands/serve.js";

const program = new Command();

program
  .name("orca")
  .description("Orca — 全能研究助手 CLI")
  .version("0.1.0");

program.addCommand(researchCommand);
program.addCommand(chatCommand);
program.addCommand(skillsCommand);
program.addCommand(serveCommand);

program.parse();
