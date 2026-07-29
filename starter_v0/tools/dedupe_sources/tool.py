from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


_TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}


def _normalized_url(value: str) -> str:
    """Return a stable URL key while preserving the original item URL."""
    raw = value.strip()
    if not raw:
        return ""

    parts = urlsplit(raw)
    if not parts.scheme or not parts.netloc:
        return raw.rstrip("/").lower()

    hostname = (parts.hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    port = parts.port
    netloc = hostname
    if port and not ((parts.scheme.lower() == "http" and port == 80) or (parts.scheme.lower() == "https" and port == 443)):
        netloc = f"{hostname}:{port}"

    query = urlencode(sorted(
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in _TRACKING_PARAMS and not key.lower().startswith("utm_")
    ))
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), netloc, path, query, ""))


def dedupe_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Remove duplicate source items, keeping the first occurrence.

    Items with URLs are deduplicated by normalized URL. Items without URLs are
    deduplicated by normalized title only when a non-empty title is present.
    """
    if items is None:
        items = []
    if not isinstance(items, list):
        raise TypeError("items must be a list of objects")

    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    duplicate_indices: list[int] = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise TypeError(f"items[{index}] must be an object")

        url_key = _normalized_url(str(item.get("url") or ""))
        title_key = " ".join(str(item.get("title") or "").lower().split())
        if url_key:
            key = ("url", url_key)
        elif title_key:
            key = ("title", title_key)
        else:
            key = ("index", str(index))

        if key in seen:
            duplicate_indices.append(index)
            continue
        seen.add(key)
        unique.append(item)

    return {
        "tool": "dedupe_sources",
        "items": unique,
        "item_count": len(unique),
        "removed_count": len(duplicate_indices),
        "duplicate_indices": duplicate_indices,
    }
