# Why Duolingo users leave: a competitive review analysis

**Data:** 174,000 Google Play reviews, US English store, newest first.
- Duolingo: 150,000 reviews, 2026-07-14 → 2026-11-23.
- Babbel, Busuu, Memrise and Speak: 6,000 newest each.

A stratified sample of 6,212 reviews was tagged by an LLM (Claude Haiku 5.5, about $0.47 in total). Tags: pain-point categories, sentiment, features mentioned, switching intent, competitor named. Duolingo shares are re-weighted back to the full review population, because the sample over-represents negative reviews. Rating and version trends use all 150k reviews.

## 1. Headline

Duolingo's store rating is still high (4.47★), but the share of 1-star reviews rose through the autumn. Release **6.106** (Nov 16) has a 1-star share of **7.0%**, against 3.4–4.5% for releases in July–September. That is the highest of the 23 releases with ≥300 reviews.

The complaints shifted toward three themes that all grew from July to November. As a share of negative (≤2★) reviews:

| Theme | Jul | Nov | Change |
|---|---|---|---|
| Streak pressure / streak-freeze problems | 7.6% | 15.5% | **2.1×** |
| Reward clutter / UI changes (chests, puzzle pieces, animations) | 5.8% | 13.7% | **2.4×** |
| Monetization / paywall (energy, Super, price) | 21.8% | 26.4% | +4.6 pp |

## 2. Why users say they're leaving

1.75% of all Duolingo reviews (weighted) say the user has left or is about to leave. The reasons they give (a review can cite more than one):

| Reason | Share of churn-intent reviews |
|---|---|
| Monetization / paywall (energy system, subscription pressure) | **43%** |
| Content quality (answers marked wrong, AI-generated errors, course changes) | 25% |
| Streak / gamification pressure | 22% |
| Ads | 20% |
| UI changes / reward clutter | 18% |
| Energy / hearts limits specifically | 18% |
| Learning effectiveness (no grammar, too game-like) | 13% |

The pattern: **the free experience got more restricted** (energy replacing hearts, freezes costing more) **at the same time as the lesson loop got noisier** (chests, puzzle events, animations). Committed learners read both changes as the app optimizing for engagement and revenue over learning.

## 3. Where they go, and why

194 competitor reviews are written by people who say they came from Duolingo:

| Destination | Ex-Duolingo reviews | Avg ★ they give the new app |
|---|---|---|
| Babbel | 72 | 4.39 |
| Speak | 66 | 4.98 |
| Busuu | 39 | 4.31 |
| Memrise | 17 | 4.59 |

What switchers praise in the new app, from the features the LLM extracted (counts):
- grammar explanations (21 counting "grammar" / "grammar lessons")
- speaking / conversation practice (16)
- structured lessons (17)
- pronunciation feedback (7)
- native-speaker audio and video
- "less gamified", no ads

In short, Duolingo loses learners who **graduate from wanting a game to wanting to learn**. Babbel and Busuu win on explanation and structure, and Speak wins on speaking practice.

## 4. Competitor weaknesses (from their own reviews)

| App | Store ★ (sample avg) | Negative share | Top pain points |
|---|---|---|---|
| Speak | 4.46 | 6% | content quality 6%, monetization 5% |
| Busuu | 4.28 | 12% | monetization 9%, content quality 7%, bugs 6% |
| Memrise | 3.52 | 36% | content quality 13%, bugs 10%, UI changes 9% |
| Babbel | 3.27 | 46% | monetization 20%, content quality 20%, bugs 12% |

Babbel attracts the most switchers but has the angriest reviews of its own, mainly about price and billing. Duolingo can win these users back with a better free learning experience. It doesn't have to match Babbel's prices.

## 5. Implications

1. Make the **core learning loop cheaper and quieter for committed learners**: practice that doesn't burn energy, and an option to collapse reward clutter.
2. Close the **explanation gap**: a little grammar explanation in the free tier is the most-cited pull factor toward competitors.
3. Fix **streak trust**: "my freeze was used even though I did my lesson" (cross-device sync) is a recurring complaint, and the streak is the habit that keeps users on Duolingo.

These become the PRD → [`PRD.md`](PRD.md).

## Method notes and limitations

- Google Play reviews skew negative and toward vocal users; they are a signal of *why*, not a measure of *how many*. The PRD's success metrics are product metrics, not review metrics.
- The 6.106 cut rests on 61 tagged negative reviews: directional only. The 1-star rate for 6.106 uses all 3,506 of its reviews.
- Competitor reviews span a longer period (newest 6,000 go back to 2024–25 for smaller apps).
- LLM tags were spot-checked by hand. The prompt and schema are in `src/label.py`.
