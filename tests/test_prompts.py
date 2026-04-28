"""Tests for prompt loader."""
import tempfile
from pathlib import Path


class TestPromptLoader:
    def test_load_existing_prompt(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")
        content = loader.load("deepresearch")
        assert content
        assert len(content) > 50

    def test_load_nonexistent_prompt(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")
        content = loader.load("nonexistent_xyz")
        assert content == ""

    def test_load_strips_front_matter(self):
        from orca.prompts.loader import PromptLoader
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "test.md"
            prompt_file.write_text("---\ntitle: Test\n---\nActual content here", encoding="utf-8")
            loader = PromptLoader(tmpdir)
            content = loader.load("test")
            assert "Actual content here" in content
            assert "---" not in content

    def test_load_caches(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")
        c1 = loader.load("deepresearch")
        c2 = loader.load("deepresearch")
        assert c1 == c2
        assert "deepresearch" in loader._cache

    def test_list_available(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")
        available = loader.list_available()
        assert "deepresearch" in available
        assert "lit" in available

    def test_clear_cache(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")
        loader.load("deepresearch")
        assert "deepresearch" in loader._cache
        loader.clear_cache()
        assert len(loader._cache) == 0
