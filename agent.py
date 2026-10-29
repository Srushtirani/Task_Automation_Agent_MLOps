import os
from ddgs import DDGS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

def search_web(topic: str, max_results: int = 6) -> list[dict]:
    """Search DuckDuckGo and return a small, normalized list of results."""
    results = []
    with DDGS() as ddgs:
        for item in ddgs.text(topic, max_results=max_results):
            title = (item.get("title") or "Untitled result").strip()
            url = (item.get("href") or item.get("url") or "").strip()
            body = (item.get("body") or "").strip()
            if url and body:
                results.append({"title": title, "url": url, "body": body})
    return results

def summarize_results(topic: str, results: list[dict]) -> str:
    """Summarize search snippets into exactly three concise bullets."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Configure it as an environment variable/secret.")

    if not results:
        raise RuntimeError("The web search returned no usable results. Try a more specific topic.")

    source_text = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['body']}"
        for r in results
    )

    llm = ChatGroq(
        model=DEFAULT_MODEL,
        temperature=0.2,
        api_key=api_key,
    )
    messages = [
        SystemMessage(content=(
            "You are a careful research assistant. Use only the supplied search results. "
            "Do not invent facts or claim you read full pages when only snippets are supplied. "
            "Return exactly three concise bullet points, each with a useful factual takeaway. "
            "If evidence is uncertain or conflicting, say so briefly. Do not add an introduction, "
            "conclusion, or extra bullets."
        )),
        HumanMessage(content=f"Research topic: {topic}\n\nSearch results:\n{source_text}\n\nReturn exactly three bullet points.")
    ]
    response = llm.invoke(messages)
    print("RAW MODEL RESPONSE:", repr(response.content))
    content = response.content
    if not isinstance(content, str):
        content = str(content)
    bullets = [line.strip() for line in content.splitlines() if line.strip()]
    bullets = [line for line in bullets if line.startswith(("-", "*", "•"))]
    if len(bullets) != 3:
        # Do not silently display malformed output as a successful three-point brief.
        raise RuntimeError(f"The model returned {len(bullets)} bullet points instead of exactly 3. Please retry.")
    return "\n".join(bullets)

def create_research_brief(topic: str) -> tuple[str, list[dict]]:
    """Sequential workflow: web search first, then LLM summarization."""
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty.")
    results = search_web(topic.strip())
    brief = summarize_results(topic.strip(), results)
    return brief, [{"title": r["title"], "url": r["url"]} for r in results]
