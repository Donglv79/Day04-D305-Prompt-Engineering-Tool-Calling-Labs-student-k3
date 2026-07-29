from __future__ import annotations

from typing import Any


def _citation(item: dict[str, Any], index: int, include_summary: bool) -> str:
    title = str(item.get("title") or "Untitled").strip()
    source = str(item.get("source") or "Unknown source").strip()
    url = str(item.get("url") or "").strip()
    summary = str(item.get("summary") or "").strip()
    link = f"[{title}]({url})" if url else title
    result = f"[{index}] {source} — {link}"
    if include_summary and summary:
        result += f" — {summary.replace(chr(10), ' ')}"
    return result


def extract_citations(
    items: list[dict[str, Any]] | None = None,
    style: str = "numbered",
    include_summary: bool = False,
) -> dict[str, Any]:
    """Create deterministic citations from already-collected research items."""
    items = [] if items is None else items
    if not isinstance(items, list):
        raise TypeError("items must be a list of objects")
    if style not in {"numbered", "markdown", "inline"}:
        raise ValueError("style must be numbered, markdown, or inline")

    citations = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise TypeError(f"items[{index - 1}] must be an object")
        citation = _citation(item, index, include_summary)
        if style == "markdown":
            citation = f"- {citation[ citation.index(']') + 2 :] if citation.startswith('[') else citation}"
        citations.append(citation)

    if style == "inline":
        markdown = " ".join(f"[{index}]" for index in range(1, len(citations) + 1))
    else:
        markdown = "\n".join(citations)
    return {
        "tool": "extract_citations",
        "citations": citations,
        "markdown": markdown,
        "citation_count": len(citations),
    }
