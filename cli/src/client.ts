/**
 * HTTP client for Orca Gateway API
 */
export class OrcaClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async runResearch(workflow: string, query: string, depth = 2, maxSources = 10): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/api/research/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflow, query, depth, max_sources: maxSources }),
    });
    return resp.json();
  }

  async getSession(sessionId: string): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/api/research/sessions/${sessionId}`);
    return resp.json();
  }

  async listWorkflows(): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/api/research/workflows`);
    return resp.json();
  }

  async searchPapers(query: string, maxResults = 10): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/api/research/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, max_results: maxResults }),
    });
    return resp.json();
  }

  async listSkills(): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/api/skills/`);
    return resp.json();
  }

  async searchSkills(query: string): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/api/skills/search?q=${encodeURIComponent(query)}`);
    return resp.json();
  }

  async health(): Promise<any> {
    const resp = await fetch(`${this.baseUrl}/health`);
    return resp.json();
  }
}
