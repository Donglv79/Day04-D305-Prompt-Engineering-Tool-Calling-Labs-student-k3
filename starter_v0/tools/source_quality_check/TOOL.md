---
name: source_quality_check
track: core
kind: local_validator
requires_env: []
inputs: [items]
outputs: [reports, item_count, average_quality_score, warning_count]
side_effect: false
---
# source_quality_check

Checks research items for URL validity, HTTPS, title, summary, and source
metadata. It returns one quality report per item and does not modify or fetch
the sources.
