from unittest.mock import patch
import pytest
import agent

def test_empty_topic_is_rejected():
    with pytest.raises(ValueError):
        agent.create_research_brief("   ")

def test_search_results_are_normalized():
    class FakeDDGS:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def text(self, topic, max_results):
            return iter([{
                "title": "Example",
                "href": "https://example.com",
                "body": "A useful snippet."
            }])
    with patch("agent.DDGS", FakeDDGS):
        result = agent.search_web("example", max_results=1)
    assert len(result) == 1
    assert result[0]["url"] == "https://example.com"
    assert result[0]["body"] == "A useful snippet."

def test_missing_groq_key_is_reported(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        agent.summarize_results("topic", [{"title": "T", "url": "https://example.com", "body": "Snippet"}])

def test_no_results_is_reported(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with pytest.raises(RuntimeError, match="no usable results"):
        agent.summarize_results("topic", [])
