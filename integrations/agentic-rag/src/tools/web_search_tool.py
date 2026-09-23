"""
Web search tool for Phase 7.

Uses Tavily, a search API designed for LLMs. Returns structured results
with title, URL, and content snippet.

Tool interface matches the Phase 4 tool contract:
    {
        "tool": "web_search",
        "ok": bool,
        "result": {"query": ..., "results": [...]},
        "summary": "...",
        "error": ...,
    }
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

_tavily_client = None


def _get_client():
    global _tavily_client
    if _tavily_client is None:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key or api_key.startswith("tvly-your"):
            raise RuntimeError(
                "TAVILY_API_KEY is not set in .env. Get a free key at https://tavily.com"
            )
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def web_search(query: str, max_results: int = 5) -> dict:
    if not query.strip():
        return {
            "tool": "web_search",
            "ok": False,
            "result": None,
            "summary": "Empty query",
            "error": "empty_query",
        }

    max_results = min(max(1, int(max_results)), 10)

    try:
        client = _get_client()
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
        )

        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:800],
            }
            for r in response.get("results", [])
        ]

        return {
            "tool": "web_search",
            "ok": True,
            "result": {"query": query, "results": results, "count": len(results)},
            "summary": f"Found {len(results)} web results for {query!r}",
            "error": None,
        }

    except Exception as e:
        return {
            "tool": "web_search",
            "ok": False,
            "result": None,
            "summary": f"Web search failed: {e}",
            "error": str(e)[:200],
        }


if __name__ == "__main__":
    print("=== Web search tool self-test ===\n")

    r1 = web_search("")
    print(f"Test 1 (empty query): {'PASS' if not r1['ok'] else 'FAIL'}")

    r2 = web_search("latest developments in retrieval augmented generation", max_results=3)
    if r2["ok"]:
        print(f"Test 2 (basic search): PASS ({r2['result']['count']} results)")
        for res in r2["result"]["results"][:2]:
            print(f"    {res['title'][:60]}")
            print(f"    {res['url']}")
    else:
        print(f"Test 2 (basic search): FAIL — {r2['error']}")

    r3 = web_search("what is RAG", max_results=20)
    if r3["ok"]:
        print(f"Test 3 (max_results cap): {'PASS' if r3['result']['count'] <= 10 else 'FAIL'}")
    else:
        print(f"Test 3 (max_results cap): SKIP — {r3['error'][:60]}")

    if r2["ok"] and r3["ok"]:
        print()
        print("All web search tests PASS")
