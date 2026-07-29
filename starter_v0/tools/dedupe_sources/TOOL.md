---
name: dedupe_sources
track: core
kind: local_transformer
requires_env: []
inputs: [items]
outputs: [items, item_count, removed_count, duplicate_indices]
side_effect: false
---
# dedupe_sources

Removes duplicate research items while preserving the first occurrence.
Items with URLs are compared using normalized URLs; URL tracking parameters
such as `utm_*`, `fbclid`, and `gclid` are ignored. Items without URLs are
compared by non-empty title. The original item objects and URLs are preserved.
