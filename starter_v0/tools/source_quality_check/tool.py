from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def _url_info(value: str) -> tuple[bool, str, bool]:
    url = value.strip()
    parsed = urlparse(url)
    valid = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    return valid, parsed.netloc.lower().removeprefix("www."), parsed.scheme == "https"


def source_quality_check(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Assess completeness and URL quality without changing source items."""
    if items is None:
        items = []
    if not isinstance(items, list):
        raise TypeError("items must be a list of objects")

    reports: list[dict[str, Any]] = []
    total_score = 0
    warning_count = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise TypeError(f"items[{index}] must be an object")

        title = str(item.get("title") or "").strip()
        summary = str(item.get("summary") or "").strip()
        source = str(item.get("source") or "").strip()
        url = str(item.get("url") or "").strip()
        valid_url, domain, is_https = _url_info(url)
        warnings: list[str] = []
        score = 0

        if valid_url:
            score += 40
        else:
            warnings.append("missing_or_invalid_url")
        if title:
            score += 25
        else:
            warnings.append("missing_title")
        if summary:
            score += 25
        else:
            warnings.append("missing_summary")
        if source:
            score += 10
        else:
            warnings.append("missing_source")
        if valid_url and not is_https:
            score = max(0, score - 10)
            warnings.append("url_is_not_https")

        warning_count += len(warnings)
        total_score += score
        reports.append({
            "index": index,
            "quality_score": score,
            "domain": domain,
            "valid_url": valid_url,
            "is_https": is_https,
            "warnings": warnings,
        })

    item_count = len(items)
    return {
        "tool": "source_quality_check",
        "reports": reports,
        "item_count": item_count,
        "average_quality_score": round(total_score / item_count, 2) if item_count else 0,
        "warning_count": warning_count,
    }
