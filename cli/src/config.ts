/**
 * CLI configuration management
 */
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

export interface OrcaCliConfig {
  gatewayUrl: string;
  defaultModel?: string;
  defaultWorkflow?: string;
}

const CONFIG_PATHS = [
  join(process.cwd(), "config.yaml"),
  join(homedir(), ".orca", "config.yaml"),
];

export function loadConfig(): OrcaCliConfig {
  for (const path of CONFIG_PATHS) {
    if (existsSync(path)) {
      try {
        const content = readFileSync(path, "utf-8");
        // Simple YAML-like parsing (key: value)
        const config: Partial<OrcaCliConfig> = {};
        for (const line of content.split("\n")) {
          const match = line.match(/^(\w+):\s*(.+)/);
          if (match) {
            const [, key, value] = match;
            if (key === "gateway_url") (config as any).gatewayUrl = value.trim();
          }
        }
        return { gatewayUrl: "http://localhost:8000", ...config };
      } catch {
        // Fall through
      }
    }
  }
  return { gatewayUrl: "http://localhost:8000" };
}
