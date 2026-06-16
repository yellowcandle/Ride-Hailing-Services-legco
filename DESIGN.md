---
name: 網約車附屬法例意見書分析報告 (sc103)
description: Bilingual investigative analysis of Hong Kong ride-hailing legislation submissions — a broadsheet brief on the public record.
colors:
  redline: "#b03a2e"
  redline-on-dark: "#d4715e"
  masthead-navy: "#1a1a2e"
  navy-raise: "#2d2d4e"
  gold-leaf: "#b8860b"
  gold-text: "#8a6608"
  verdict-green: "#1a7045"
  warm-paper: "#faf8f5"
  card: "#ffffff"
  ink-body: "#3a3630"
  rule: "#e3ddd3"
  rule-2: "#ece7df"
  navy-rule: "#3a3a52"
  navy-line: "#2a2a40"
  header-tint: "#f0ece4"
  quote-tint: "#fdf9ee"
  ink-muted: "#6b6557"
  ink-faint: "#8a8578"
typography:
  masthead:
    fontFamily: '"MetroSung", "Noto Serif HK", "Noto Serif TC", serif'
    fontSize: "clamp(2.1rem, 6vw, 4.4rem)"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "0.01em"
  statement:
    fontFamily: '"MetroSung", "Noto Serif HK", "Noto Serif TC", serif'
    fontSize: "clamp(1.55rem, 3.6vw, 2.6rem)"
    fontWeight: 400
    lineHeight: 1.3
  section:
    fontFamily: '"MetroSung", "Noto Serif HK", "Noto Serif TC", serif'
    fontSize: "clamp(1.35rem, 2.6vw, 1.9rem)"
    fontWeight: 400
    lineHeight: 1.2
  subhead:
    fontFamily: '"MetroSung", "Noto Serif HK", "Noto Serif TC", serif'
    fontSize: "1.1rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: '"PingFang HK", "PingFang TC", "Microsoft JhengHei", "Noto Sans HK", sans-serif'
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.85
  data:
    fontFamily: '"MetroSung", "Noto Serif HK", "Noto Serif TC", serif'
    fontSize: "clamp(1.8rem, 4vw, 2.6rem)"
    fontWeight: 400
    lineHeight: 1.0
  label:
    fontFamily: '"PingFang HK", "PingFang TC", "Microsoft JhengHei", "Noto Sans HK", sans-serif'
    fontSize: "0.82rem"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  bar: "6px"
  panel: "4px"
  md: "8px"
  card: "10px"
  pill: "99px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  section: "40px"
components:
  masthead:
    backgroundColor: "{colors.masthead-navy}"
    textColor: "#ffffff"
    padding: "52px 0 44px"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.masthead-navy}"
    rounded: "{rounded.card}"
    padding: "30px 34px"
  feature-panel:
    backgroundColor: "{colors.masthead-navy}"
    textColor: "#ffffff"
    rounded: "{rounded.panel}"
    padding: "46px 52px"
  table-header:
    backgroundColor: "{colors.header-tint}"
    textColor: "{colors.masthead-navy}"
    padding: "9px 12px"
  pullquote:
    backgroundColor: "{colors.quote-tint}"
    textColor: "{colors.masthead-navy}"
    rounded: "{rounded.md}"
    padding: "28px 32px"
  tag-loosen:
    backgroundColor: "#e8f3ec"
    textColor: "{colors.verdict-green}"
    rounded: "{rounded.pill}"
    padding: "2px 9px"
  tag-tighten:
    backgroundColor: "#f9e9e6"
    textColor: "{colors.redline}"
    rounded: "{rounded.pill}"
    padding: "2px 9px"
  tag-redesign:
    backgroundColor: "#fdf3dc"
    textColor: "{colors.gold-text}"
    rounded: "{rounded.pill}"
    padding: "2px 9px"
---

# Design System: 網約車附屬法例意見書分析報告 (sc103)

## 1. Overview

**Creative North Star: "The Broadsheet Brief"**

This is a Hong Kong serious-press analysis given a screen. It reads like the front matter of
a quality newspaper's investigative feature: a deep navy masthead carrying the title in a
Ming/Song serif, a warm paper ground beneath the body, and a single contested red that the editor
reaches for only to mark where the argument is joined. The authority is earned, not asserted — the
design steps back so the numbers, the stance tallies, and the document citations carry the weight.

The system is **flat and structured by line**, not by shadow. Depth comes from 1px warm rules,
tonal fills, and the navy masthead/feature panel against the paper field — the way ink sits on
newsprint. It is **editorial and confident**: a real verdict in the lede, decisive pull-quotes, and
data visualisation with presence (the stance bar, the dark cross-holding matrix). Traditional
Chinese is the primary script; everything is tuned for comfortable CJK reading at a generous 1.85
line-height, with English handled gracefully where the sources demand it.

It explicitly rejects three things, drawn straight from the brief: the **partisan/clickbait**
register (no alarm-colour theatrics — the edge is in the findings, not the decoration), the
**generic AI dashboard** (no cards-everywhere reflex, no gradient-hero-plus-stat-grid SaaS
template, no stacked drop-shadows), and the **government/corporate PDF** (no stiff 官方 block
layout, no walls of undifferentiated gray, no hierarchy-free density). This is meant to be *read*,
not filed.

**Key Characteristics:**
- Navy masthead + warm paper ground + one contested red, used sparingly.
- Ming/Song serif for display, CJK sans for body — a deliberate two-register pairing.
- Flat surfaces; depth from line and tone, not shadow.
- Editorial hierarchy: verdict first, evidence second, stakeholder background third.
- Every claim sits beside its document number; sourcing is visible.

## 2. Colors

A sober broadsheet palette: authoritative navy and warm paper carry the page, with a single
contested red and a brass gold reserved for marking where stances diverge. **Each accent has a
light-ground form and, where it appears on the navy panel, a lighter on-dark form** — so contrast
holds in both worlds.

### Primary
- **Redline** (#b03a2e): The contested red — a cinnabar/brick terracotta. The accent on light
  grounds: hyperlinks, the headline stat numbers, the "oppose / tighten" stance, the lede teaser,
  and the summary verdict. It marks where the argument is joined; its restraint is what gives it weight.
- **Redline-on-Dark** (#d4715e): The legible form of the redline **on the navy panel** — kicker
  labels (背景調查 · 的士業界, 意見書分析) and the filled cross-holding-matrix markers. Use this, not
  the base redline, for any red text or marker on `masthead-navy` (the base red fails contrast there).

### Secondary
- **Verdict Green** (#1a7045): The "support / loosen" stance — stance bar, `tag-loosen` chip, and
  the positive cells in the position table.
- **Gold Leaf** (#b8860b): The "redesign / caution" register, **as a fill only** — the stance-bar
  segment, legend swatch, and the matrix's outline marker ring.
- **Gold-Text** (#8a6608): The text form of the gold register. Use it wherever gold is *text* —
  the `tag-redesign` label and the position table's `.mid` cells. The brass `gold-leaf` fails
  contrast as text on light tints; `gold-text` is the readable substitute.

### Neutral
- **Masthead Navy** (#1a1a2e): The masthead and feature-panel ground, and the colour of headings.
- **Navy Raise** (#2d2d4e): The lifted navy — one notch warmer/lighter than the body ink, used
  for emphasis where a softer ink is wanted.
- **Warm Paper** (#faf8f5): The body background. The committed paper ground of the broadsheet;
  not decorative warmth, but the field the ink sits on.
- **Card White** (#ffffff): Raised reading surfaces — cards, table cells.
- **Ink Body** (#3a3630): The body text colour — a warm near-black at ~11:1 on warm paper. Body
  copy lives here, **not** at the muted/faint grays.
- **Rule** (#e3ddd3) / **Rule-2** (#ece7df): The 1px warm dividers — table borders, card outlines,
  card-header and group-head hairlines, the footer rule. Line, not shadow, separates things.
- **Navy Rule** (#3a3a52) / **Navy Line** (#2a2a40): The dividers *inside* the navy panel/masthead
  (edition rule, dateline, TOC nav, matrix row lines).
- **Header Tint** (#f0ece4) / **Quote Tint** (#fdf9ee): Tonal fills for table headers and pull-quotes.
- **Ink Muted** (#6b6557): Secondary and **citation** text — figure labels, card meta, the
  `[CB(3)…]` document numbers (≥4.5:1 on light). **Ink Faint** (#8a8578): decorative / dark-panel
  labels only; never as body text on light.

### Named Rules
**The Redline Rule.** The contested red is reserved for where stances diverge — the accent, links,
oppose/tighten stance, the verdict. Never a general-purpose highlight or decorative fill. Its
rarity is what makes a reader's eye trust it.

**The Three-Stance Rule.** Green = loosen/support, Red = tighten/oppose, Gold = redesign/caution.
Fixed across stance bar, tags, and the position table. Never recolour a stance for variety, and
never let colour be the *only* signal — every stance cue carries a text label, and a `標籤圖例` key
is repeated where the tags reappear.

**The On-Dark Rule.** On the navy ground, swap to the legible variants: `redline-on-dark` for any
red text/marker, light neutrals (#c9c4b8 / #9a9486) for labels. The base `redline` and `gold-text`
are light-ground colours; they fail on navy.

**The Gold-Is-A-Fill Rule.** `gold-leaf` (#b8860b) is for fills (bar segment, swatch, marker ring),
never for text. Gold text uses `gold-text` (#8a6608).

## 3. Typography

**Display Font:** MetroSung — a Traditional-Chinese Ming/Song serif (self-hosted, subset to a
~268KB WOFF2, `font-display: swap`), with `Noto Serif HK / Noto Serif TC` as the fallback chain.
**Body Font:** a CJK system sans stack — `"PingFang HK", "PingFang TC", "Microsoft JhengHei",
"Noto Sans HK", sans-serif`.

**Character:** A deliberate two-register pairing on a contrast axis — a Ming/Song *serif* for
display (the authority of a newspaper masthead) over a clean *sans* for the reading column. The
serif carries the title, the section heads, the lede statement, the feature-panel title, the big
figures, and the pull-quotes; everything else is the sans. The pairing is the broadsheet's voice.

### Hierarchy
- **Masthead** (serif, clamp 2.1→4.4rem, lh 1.15): The report title, white on the navy nameplate.
- **Statement** (serif, clamp 1.55→2.6rem, lh 1.3): The lede verdict — the page's strongest sentence.
- **Section** (serif, clamp 1.35→1.9rem): `h2` section heads (一/二/三/四), beside a serif redline numeral.
- **Subhead** (serif, 1.1rem): `.group-head` — stakeholder groups (甲/乙/丙…) and Part-四 subjects.
- **Body** (sans, 1.0625rem, lh 1.85): The reading column. Generous leading tuned for Traditional
  Chinese; prose measures capped ~70ch.
- **Data** (serif, clamp 1.8→2.6rem): The lede figures (≈90% / ≈76% / 430) and legend counts.
- **Label** (sans, 0.82rem): Metadata, edition/dateline, TOC nav, citations, captions.

### Named Rules
**The Serif-Display / Sans-Body Rule.** Display is MetroSung serif; the reading column and all
labels are the CJK sans. Don't blur the line — body copy never goes serif, and UI labels (nav,
tags, meta) never go display. The two registers are the pairing; collapsing them flattens the voice.

**The CJK Leading Rule.** Body copy runs at 1.85 line-height. Traditional Chinese needs the air;
never tighten the body below 1.6, and never apply Latin-tuned leading (~1.4) to the Chinese column.

## 4. Elevation

The system is **flat by intent**. Depth is conveyed by 1px warm rules (#e3ddd3), tonal fills
(header tint, quote tint, even-row stripe), and the navy masthead/feature panel sitting against the
warm-paper ground — the logic of ink on newsprint, not floating panels. Cards carry only a
barely-there ambient shadow to lift them off the paper; it is a whisper, not a structural device.

### Shadow Vocabulary
- **Paper Lift** (`box-shadow: 0 1px 3px rgba(0,0,0,0.04)`): The resting card shadow. On hover the
  card border warms (`rule` → `rule-2`) and the shadow grows a hair (`0 2px 6px rgba(0,0,0,0.06)`)
  — the only state animation, ~180ms ease-out.

### Named Rules
**The Line-Not-Shadow Rule.** Separation is done with a 1px warm rule or a tonal fill, never with
elevation. Stacked or blurred shadows read as the AI-dashboard look this report rejects.

## 5. Components

Components read like a well-designed feature article: the data viz has presence, tables and tags
do the analytical work, ornament is kept to what earns its place. **No element uses a `border-left`
or `border-right` accent stripe** — accents are full borders, top rules, or background tints.

### Masthead + TOC (signature)
- Flat `masthead-navy` nameplate (no gradient). An edition rule (source label + `意見書分析` in
  `redline-on-dark`) over the serif title, a light deck, a bordered dateline, and a **TOC nav strip**
  (`一 整體立場 / 二 持份者 / 三 取態總表 / 四 背景調查`) linking to `#s1–#s4`. A single masthead
  entrance (title rises+fades, deck follows) gated behind `prefers-reduced-motion: no-preference`.

### Section Heading (signature)
- A **full-width 2px `masthead-navy` top rule**, then a row of a serif **Chinese numeral**
  (一/二/三/四) in `redline` + the serif title + a small muted meta label. Each `<h2>` carries a
  visually-hidden `第N部分 ·` for screen readers. This top-rule-plus-numeral *is* the broadsheet
  section marker — there is no left stripe.

### Lede (signature, replaces stat tiles)
- An asymmetric two-column opener (stacks below 960px): the serif verdict **statement** + a body
  deck with colour-coded `太鬆`/`太緊`, beside a **hairline-separated figure column** (≈90% redline,
  ≈76%, 430) — figures on rules, not boxed stat tiles. A one-line **lede teaser** links to the
  owner-circle finding (`#s4`).

### Stance Bar (signature)
- A single 48px segmented bar (6px radius), segments by the Three-Stance mapping; the dominant
  segment carries an inline label in `masthead-navy` ink (full label on desktop, a short `83%` on
  mobile). Always paired with a bordered **legend** (swatch + label + description + serif count), so
  stance is never colour-only.

### Cross-Holding Matrix + Dark Feature Panel (signature showpiece)
- A `masthead-navy` feature panel (4px radius) reserved for the investigative climax. Inside: a
  `redline-on-dark` kicker, serif white title, deck, and a **cross-holding matrix** — a grid of
  people × organisations with markers: **filled** (`redline-on-dark`) = holds a senior post,
  **outline** (gold ring) = founding-member body, **dot** (faint) = none. On mobile (≤600px) the
  matrix **stacks**: each person becomes a block listing org-labelled membership rows (no horizontal
  scroll). A local legend + supporting prose follow.

### Cards / Containers
- Card White, 1px `rule` border, 10px radius, Paper Lift shadow, ~30px 34px padding. A `card-header`
  (org name + meta + stance tags over a 1px `rule-2`) then the bullet content. **Group rhythm:**
  each `.group-head` opens with a full-width 1px `rule` top hairline (the first per section has
  none) to break long card stacks. Never nest a card in a card.

### Tags / Chips + Legend
- Pill (99px), 0.75rem, tinted fill + matching 1px border + matching text colour, by stance:
  `tag-loosen` (verdict-green text), `tag-tighten` (redline text), `tag-redesign` (**gold-text**).
  Always text-labelled. A compact `標籤圖例` key repeats the mapping above Parts 二 and 三.

### Tables
- Header Tint fill (600 weight); Card White cells; 1px `rule` grid; even rows striped #fbfaf7;
  wrapped in `.scroll-x` (min-width) so they scroll rather than break on mobile. The position table
  states stance in **AA-coloured text** (正面 / 負面 / 部分負面) — no emoji.

### Pull-quotes
- **Featured:** Quote Tint fill, an oversized serif `"` **on the left** (redline), serif quote, a
  cite line with a redline rule + `ink-muted` document number. **Others:** `quote-item` cards with a
  small `::before` quote glyph, full 1px border (no stripe); an `opposing` variant for 反方 voices.

### Footer
- `ink-muted` text above a 2px `masthead-navy` top rule — methodology, sources, and a back-to-top link.

## 6. Do's and Don'ts

### Do:
- **Do** keep the document citation beside every claim — `[CB(3)662/2026(NNN)]` in `ink-muted`
  (≥4.5:1). Visible sourcing is the product; it is non-negotiable.
- **Do** reserve Redline for the contested-point accent, and switch to **Redline-on-Dark** for any
  red text/marker on the navy panel — **The On-Dark Rule**.
- **Do** use **Gold-Text (#8a6608)** wherever gold is text, and keep **Gold-Leaf (#b8860b)** for
  fills only — **The Gold-Is-A-Fill Rule**.
- **Do** hold the Three-Stance mapping fixed, pair colour with a text label, and repeat the
  `標籤圖例` key where tags recur — stance must survive colour-blindness and grayscale.
- **Do** set display in MetroSung serif and the reading column in the CJK sans — **The
  Serif-Display / Sans-Body Rule** — and run body at 1.85 line-height.
- **Do** separate elements with a 1px warm rule or a tonal fill — **The Line-Not-Shadow Rule**.

### Don't:
- **Don't** drift toward the **partisan / clickbait** look — no alarm-colour theatrics, no tabloid
  styling. The edge comes from the findings, not the decoration.
- **Don't** fall into the **generic AI dashboard** — no cards-everywhere reflex, no
  gradient-hero-plus-stat-grid, no stacked drop-shadows. The lede is editorial, not a stat grid.
- **Don't** produce a **government / corporate PDF** — no stiff 官方 block layout, no walls of
  undifferentiated gray, no hierarchy-free density. This is read, not filed.
- **Don't** use a `border-left`/`border-right` colour stripe as a section or card marker — the
  section marker is a top rule + numeral; accents are full borders or top rules.
- **Don't** set Ink Faint (#8a8578) or Ink Muted as **body** text on warm paper, or the base Redline
  / Gold-Leaf as text where they fail contrast — body stays at Ink Body (#3a3630).
- **Don't** put body copy in the serif or UI labels in the display face, and don't nest a card in a card.
