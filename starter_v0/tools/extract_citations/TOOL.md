---
name: extract_citations
track: core
kind: local_formatter
requires_env: []
inputs: [items, style, include_summary]
outputs: [citations, markdown, citation_count]
side_effect: false
---
# extract_citations

Creates numbered, markdown-list, or inline citations from existing research
items. It does not fetch, verify, or invent source information.
