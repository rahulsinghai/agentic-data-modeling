"""Unit tests for config."""

from pathlib import Path

from agentic_data_modeling.config import Settings, get_settings


class TestConfig:
    def test_defaults(self):
        s = Settings(openai_api_key="test-key")
        assert s.model == "gpt-4o-mini"
        assert s.output_dir == Path("output")
        assert s.temperature == 0.0

    def test_get_settings_override(self):
        s = get_settings(openai_api_key="override-key", model="gpt-4o")
        assert s.openai_api_key == "override-key"
        assert s.model == "gpt-4o"
