# Why Duolingo users leave: LLM-powered review analysis → PRD

**Live report:** https://eloisehe.here/app-review-insights/report/
**Docs:** [Competitive analysis](docs/competitive_analysis.md) · [PRD: Focus Mode](docs/PRD.md)

This project scrapes 174,000 Google Play reviews of Duolingo and four competitors (Babbel, Busuu, Memrise, Speak) and tags a stratified sample with an LLM: pain-point category, sentiment, features mentioned and switching intent. It tracks pain points month by month and release by release, ties rating drops to specific versions, and turns the findings into a full product requirements doc.

## Key findings

- **Release 6.106 (Nov 16, 2026) has the highest 1-star share of the last 23 releases (7.0%),** against 3.4–4.5% for July–September releases.
- **Complaints shifted toward the engagement layer.** As a share of negative reviews from July to November, streak complaints went 7.6% → 15.5% (2.1×) and reward-clutter / UI complaints 5.8% → 13.7% (2.4×). Monetization stayed the largest theme (21.8% → 26.4%).
- **Why users leave:** among churn-intent reviews, 43% cite monetization / paywall, 25% content quality, 22% streak pressure, 20% ads and 18% reward clutter.
- **Where they go:** 194 competitor reviews come from ex-Duolingo users: Babbel 72, Speak 66, Busuu 39, Memrise 17. They praise **grammar explanations**, **speaking practice**, structure and fewer interruptions.
- **Competitor gap:** Babbel attracts the most switchers but is the most-criticized itself (46% negative, mostly price and billing). Duolingo can win these users back with a better free learning experience, without matching Babbel's prices.

→ **PRD: Focus Mode**, an opt-in learning-first mode for committed free learners:
- P0: quiet rewards, and a streak you can trust.
- P1: free "why?" grammar explanations, and practice that doesn't cost energy.

Primary metric is D30 retention (+1 pp), with Super conversion and revenue per DAU as guardrails. The A/B test needs about 32.7k users per arm.

## Pipeline

```
src/scrape.py        google-play-scraper → data/raw/*.json  (Duolingo 150k newest, competitors 6k each)
src/build_sample.py  stratified sample: Duolingo month × star-bucket cells (with weights),
                     plus every competitor review that mentions Duolingo, plus 250 random per competitor
src/label.py         Claude (structured outputs, Pydantic schema) tags 40 reviews per call → data/labels.jsonl
src/analyze.py       weighted pain-point shares, monthly + per-release trends, churn reasons,
                     switcher destinations, competitor pain points → report/data.json
src/build_report.py  inlines the data into report/index.html
```

**LLM tagging**
- Model: `claude-haiku-5-5`, with output schema-constrained by `messages.parse`.
- Volume: 6,212 reviews in 154 calls, about $0.47 in total.
- Each review gets:
  - `sentiment`
  - `pain_points` (12 fixed categories)
  - `features` (free text)
  - `switching` (`none` / `considering` / `switched_away` / `switched_from_duolingo`)
  - `competitor_mentioned`
- Labels were spot-checked by hand.

**Why a stratified sample:** most Duolingo reviews are short 5-star reviews ("good app"). Sampling evenly across month × star bucket keeps enough negative reviews in every month to track trends. Each sampled review carries a weight (cell size / sample size), so shares are projected back to the full review population.

## Limitations

- Reviews are self-selected and skew negative. They explain *why* users leave, not *how many*.
- Release-level pain-point mixes rest on small tagged samples (61 negative reviews for 6.106), so they're directional. The release 1-star rates use all reviews.
- Raw review text isn't committed, to respect Google Play's terms. `labels.jsonl` holds review IDs and tags only. Re-run `scrape.py` to rebuild.

## Reproduce

```bash
pip install -r requirements.txt
python src/scrape.py           # ~15 min
python src/build_sample.py
export ANTHROPIC_API_KEY=...   # labeling costs well under $1 with Haiku
python src/label.py            # resumable
python src/analyze.py && python src/build_report.py
```
