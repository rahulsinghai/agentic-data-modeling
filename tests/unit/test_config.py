"""Unit tests for config."""

from pathlib import Path

from agentic_data_modeling.config import Settings, get_settings


class TestConfig:
    def test_defaults(self):
        s = Settings(anthropic_api_key="test-key")
        assert s.model == "claude-sonnet-4-6-20250514"
        assert s.output_dir == Path("output")
        assert s.temperature == 0.0

    def test_get_settings_override(self):
        s = get_settings(anthropic_api_key="override-key", model="claude-opus-4-6-20250514")
        assert s.anthropic_api_key == "override-key"
        assert s.model == "claude-opus-4-6-20250514"
