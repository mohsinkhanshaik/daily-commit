# AI Pulse - Roadmap

AI Pulse turns daily AI-industry research into a queryable archive plus a stdlib-only Python toolkit, built one feature per day through a full issue -> PR -> review -> merge cycle.

Layout: digests/YYYY-MM-DD.md holds each day's researched digest. src/aipulse/ holds the toolkit, one module per day.

Rule: Day N is done when its module exists in src/aipulse/. The daily run picks the lowest N whose module is missing, implements it, and ships that day's digest alongside it.

Phase 1 - Foundations
Day 1 - models.py - Core dataclasses: Category, NewsItem, Digest
Day 2 - digest_parser.py - Parse digest markdown into model objects
Day 3 - tagger.py - Rule-based topic tagging for news items
Day 4 - entities.py - Company and model name extraction via lexicon
Day 5 - archive.py - Scan digests/ and build a JSON index

Phase 2 - Analysis
Day 6 - trends.py - Term frequency across time windows
Day 7 - scoring.py - Importance scoring for news items
Day 8 - timeline.py - Per-entity event timelines
Day 9 - stats.py - Weekly aggregates and category counts
Day 10 - search.py - Ranked keyword search across the archive

Phase 3 - Insight
Day 11 - momentum.py - Rising and falling topics week over week
Day 12 - cooccur.py - Entity co-occurrence pairs
Day 13 - summarize.py - Extractive digest-of-digests
Day 14 - compare.py - Compare two date ranges
Day 15 - render.py - Markdown report renderer

Phase 4 - Product
Day 16 - cli.py - argparse CLI over the toolkit
Day 17 - weekly.py - Weekly report generator
Day 18 - dedupe.py - Near-duplicate story detection
Day 19 - validate.py - Digest format linter
Day 20 - export.py - CSV and JSON exporters

Phase 5 - Depth
Day 21 - watchlist.py - Track chosen companies and models
Day 22 - glossary.py - Auto-glossary of recurring terms
Day 23 - sentiment.py - Lexicon-based tone scoring
Day 24 - graphs.py - ASCII trend charts
Day 25 - alerts.py - Threshold-based highlights
Day 26 - cache.py - Index caching layer
Day 27 - config.py - Central configuration
Day 28 - tests_core.py - Tests for models, parser, tagger
Day 29 - tests_analysis.py - Tests for scoring and trends
Day 30 - docs.py - README generator from roadmap and archive

After Day 30: propose the next feature in each day's issue and keep numbering.
