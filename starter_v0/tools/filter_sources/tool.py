from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def _domain(url: str) -> str:
    hostname = (urlparse(url.strip()).hostname or "").lower()
    return hostname.removeprefix("www.")


def _domain_allowed(domain: str, allowed_domains: list[str]) -> bool:
    return any(domain == candidate or domain.endswith("." + candidate) for candidate in allowed_domains)


def filter_sources(
    items: list[dict[str, Any]] | None = None,
    allowed_domains: list[str] | None = None,
    keyword: str = "",
    https_only: bool = False,
    min_summary_length: int = 0,
) -> dict[str, Any]:
    """Filter existing research items using explicit, deterministic criteria."""
    items = [] if items is None else items
    allowed_domains = allowed_domains or []
    if not isinstance(items, list):
        raise TypeError("items must be a list of objects")
    if not isinstance(allowed_domains, list) or not all(isinstance(value, str) for value in allowed_domains):
        raise TypeError("allowed_domains must be a list of strings")
    if min_summary_length < 0:
        raise ValueError("min_summary_length must be non-negative")

    normalized_domains = [value.strip().lower().removeprefix("www.") for value in allowed_domains if value.strip()]
    normalized_keyword = keyword.strip().lower()
    kept: list[dict[str, Any]] = []
    excluded_indices: list[int] = []
    exclusion_reasons: dict[str, int] = {}

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise TypeError(f"items[{index}] must be an object")
        url = str(item.get("url") or "").strip()
        domain = _domain(url)
        summary = str(item.get("summary") or "").strip()
        searchable = " ".join(str(item.get(field) or "") for field in ("title", "summary", "source")).lower()
        reason = ""
        if normalized_domains and not _domain_allowed(domain, normalized_domains):
            reason = "domain_not_allowed"
        elif https_only and not url.lower().startswith("https://"):
            reason = "not_https"
        elif normalized_keyword and normalized_keyword not in searchable:
            reason = "keyword_not_found"
        elif len(summary) < min_summary_length:
            reason = "summary_too_short"

        if reason:
            excluded_indices.append(index)
            exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
        else:
            kept.append(item)

    return {
        "tool": "filter_sources",
        "items": kept,
        "item_count": len(kept),
        "excluded_count": len(excluded_indices),
        "excluded_indices": excluded_indices,
        "exclusion_reasons": exclusion_reasons,
    }
