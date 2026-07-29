---
name: filter_sources
track: core
kind: local_transformer
requires_env: []
inputs: [items, allowed_domains, keyword, https_only, min_summary_length]
outputs: [items, item_count, excluded_count, excluded_indices, exclusion_reasons]
side_effect: false
---
# filter_sources

Filters existing research items by allowed domain, keyword, HTTPS requirement,
and minimum summary length. It does not fetch or modify source items.
