# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A bilingual (primary `zh-Hant-HK`) **data-journalism archive + analysis**, not a software
project. There is no build/lint/test system. It covers public submissions to the HK LegCo
subcommittee **sc103** (與規管網約車服務有關的4項附屬法例小組委員會) on ride-hailing
subsidiary legislation: ~1,135 individual + ~20 organisation submissions across paper series
CB(3)662/673/688/710 (plus org papers 634/641/662).

Published report (GitHub Pages): https://yellowcandle.github.io/Ride-Hailing-Services-legco/

Primary audience: HK public and journalists, on mobile, reading Traditional Chinese.

## Data pipeline (manual steps, no build system)

1. **Source feed (JSON)** — the LegCo `d.json` endpoint (URL in `README.md` and the header of
   `submissions/INDEX.md`). Re-fetch to pick up new batches; LegCo kept posting batches after
   the 2026-06-15 deadline (snapshots are dated).
2. **Download PDFs** → `submissions/*.pdf`.
3. **Extract text** → `submissions/md/*.md` via **markitdown**. (`submissions/md/*.err` is the
   extraction stderr and is gitignored.)
4. **Scanned/image PDFs** markitdown can't read → OCR with `ocr_710_11.py` (PaddleOCR
   `chinese_cht`). It installs a `langchain` meta-path stub so PaddleOCR imports without
   downgrading the user's langchain — see the file docstring before reusing/editing it.
5. **Analysis** is hand-written in `submissions/ANALYSIS.md` (+ `ANALYSIS.html`); the
   paper-number → file manifest is `submissions/INDEX.md`.
6. **Published report** `docs/index.html` is hand-authored single-file HTML, served by GitHub
   Pages, using `docs/fonts/MetroSung-subset.woff2`. `MetroSung.otf` (root) is the full font.

## File / naming conventions

- `sc103cb3-{paper}-{c|ec}.pdf`:
  - `-c` = a single Chinese-only document (usually an organisation submission).
  - `-{range}-ec` = a bundled volume of many individual submissions, e.g. `-101-150-ec`.
- Each PDF has a matching `submissions/md/<same-stem>.md`.
- `只限委員參閱` (members-only) entries appear in `INDEX.md` but have **no public file or text**.

## Editorial rules (when touching analysis or the report)

From `PRODUCT.md` and `DESIGN.md`:

- Every claim carries its paper number / citation inline. Flag unverified items plainly
  (`未能核實`, `查無實體`). The rigour is what licenses the pointed, investigative tone.
- Encode stance with **text labels, not colour alone** (colour-blind readers; target WCAG 2.1 AA).
- Primary language is `zh-Hant-HK`; tune typography for CJK reading. Use English only where the
  sources are in English.
- Keep snapshot dates honest. State coverage and what is members-only / unreadable rather than
  implying full coverage.

## Note on tooling directories

`.claude/`, `.cursor/`, `.agents/`, `.gemini/`, `.kiro/`, `.qoder/`, `.opencode/`, `.impeccable/`
hold a vendored `impeccable` design skill (and other agent configs), **not** project content.
Ignore them when reasoning about the archive itself.
