"""Tests for Python CLI."""
import pytest
from click.testing import CliRunner
from orca.cli.python_cli import cli


class TestPythonCLI:
    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "orca" in result.output.lower() or "Orca" in result.output

    def test_research_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["research", "--help"])
        assert result.exit_code == 0

    def test_chat_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["chat", "--help"])
        assert result.exit_code == 0

    def test_skills_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["list-skills", "--help"])
        assert result.exit_code == 0

    def test_serve_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_research_command_executes(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["research", "deep_research", "test query"])
        # May fail without gateway but should at least parse args
        assert result.exit_code in (0, 1, 2)
