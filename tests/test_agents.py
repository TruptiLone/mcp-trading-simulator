import importlib.util
import pytest

@pytest.mark.skipif(importlib.util.find_spec("agents") is None, reason="optional agents extra not installed")
def test_optional_providers_are_lazy(monkeypatch):
    for key in ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "GOOGLE_API_KEY", "GROK_API_KEY", "OPENROUTER_API_KEY"]:
        monkeypatch.delenv(key, raising=False)
    from backend.traders import get_model
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        get_model("gpt-4o-mini")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    assert get_model("gpt-4o-mini") == "gpt-4o-mini"
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        get_model("gemini-test")
