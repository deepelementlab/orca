"""Orca Python CLI — 直接调用 ResearchEngine."""
from __future__ import annotations
import asyncio
import logging
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from orca.config.orca_config import OrcaConfig

console = Console()
logger = logging.getLogger(__name__)

def _load_config(config_path: str | None) -> OrcaConfig:
    if config_path:
        return OrcaConfig.from_yaml(config_path)
    return OrcaConfig()

@click.group()
@click.option("--config", "-c", default=None, help="Path to config.yaml")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config: str | None, verbose: bool):
    """Orca — 全能研究助手 CLI."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = _load_config(config)
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

@cli.command()
@click.argument("workflow")
@click.argument("query")
@click.option("--depth", "-d", default=2, help="Research depth (1-5)")
@click.option("--max-sources", "-s", default=10, help="Maximum sources")
@click.option("--format", "-f", "output_format", default="markdown", help="Output format")
@click.pass_context
def research(ctx, workflow: str, query: str, depth: int, max_sources: int, output_format: str):
    """Execute a research workflow. WORKFLOW: deep_research|lit_review|paper_audit|source_compare|peer_review|paper_writing|replication|eli5|session_search"""
    from orca.research.engine import ResearchEngine
    config = ctx.obj["config"]
    engine = ResearchEngine(config=config.research)

    async def _run():
        await engine.initialize()
        result = await engine.execute(workflow=workflow, query=query, depth=depth,
                                     max_sources=max_sources, output_format=output_format)
        if result.error:
            console.print(f"[red]Error:[/red] {result.error}")
            sys.exit(1)
        console.print(Panel(Markdown(result.summary), title=f"Research: {workflow}"))
        if result.sources:
            console.print(f"\n[dim]Based on {len(result.sources)} sources | Confidence: {result.confidence_score:.0%}[/dim]")

    asyncio.run(_run())

@cli.command()
@click.argument("query")
@click.pass_context
def chat(ctx, query: str):
    """Send a chat query to the Orca agent."""
    async def _run():
        try:
            from orca.agent.graph import make_lead_agent
            from langchain_core.messages import HumanMessage

            agent = make_lead_agent()
            result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
            for msg in result.get("messages", []):
                content = getattr(msg, "content", None)
                if content and hasattr(msg, "type") and msg.type == "ai":
                    console.print(Panel(Markdown(content), title="Orca"))
                    return
            console.print("[dim]No response generated.[/dim]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            console.print("[dim]Chat mode may require LLM configuration. Set ORCA_LLM_API_KEY in config.[/dim]")

    asyncio.run(_run())

@cli.command(name="list-skills")
@click.pass_context
def list_skills(ctx):
    """List available skills in the market."""
    from orca.skills.market import SkillMarket
    config = ctx.obj["config"]
    market = SkillMarket(skills_dir=config.skills_dir)
    skills = market.list_skills()
    if not skills:
        console.print("[yellow]No skills found.[/yellow]")
        return
    for skill in skills:
        console.print(f"  • [green]{skill['name']}[/green] — {skill.get('description', '')}")

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind")
@click.option("--port", "-p", default=8000, help="Port to bind")
@click.pass_context
def serve(ctx, host: str, port: int):
    """Start the Orca Gateway server."""
    import uvicorn
    from orca.gateway.app import create_app
    config = ctx.obj["config"]
    app = create_app(config)
    console.print(f"[green]Starting Orca Gateway on {host}:{port}[/green]")
    uvicorn.run(app, host=host, port=port)

@cli.command()
@click.pass_context
def workflows(ctx):
    """List available research workflows."""
    from orca.research.engine import ResearchEngine
    config = ctx.obj["config"]
    engine = ResearchEngine(config=config.research)

    async def _run():
        await engine.initialize()
        wfs = engine.list_workflows()
        for wf in wfs:
            console.print(f"  • [cyan]{wf['name']}[/cyan] ({wf['category']}) — {wf['description']}")

    asyncio.run(_run())

if __name__ == "__main__":
    cli()
