import requests


def web_search(query: str) -> str:
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=15,
        )
        data = resp.json()
        results = []
        for topic in data.get("RelatedTopics", [])[:5]:
            if "Text" in topic:
                results.append(topic["Text"])
            elif "Topics" in topic:
                for sub in topic["Topics"][:3]:
                    if "Text" in sub:
                        results.append(sub["Text"])
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search failed: {e}"


def fetch_url(url: str) -> str:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        text = resp.text[:4000]
        return text
    except Exception as e:
        return f"Failed to fetch URL: {e}"


WEB_TOOLS = [
    (web_search, "web_search", "Search the web for information", {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
        },
        "required": ["query"],
    }),
    (fetch_url, "fetch_url", "Fetch the content of a URL", {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
        },
        "required": ["url"],
    }),
]
