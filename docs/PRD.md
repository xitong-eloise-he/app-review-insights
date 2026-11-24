# PRD: Focus Mode, a learning-first Duolingo for committed learners

| | |
|---|---|
| **Author** | Eloise He (portfolio exercise; not affiliated with Duolingo) |
| **Status** | Draft for discussion |
| **Evidence** | [Competitive review analysis](competitive_analysis.md): 174k Google Play reviews, 6.2k LLM-tagged |

## 1. Problem

Duolingo's most committed users, the ones with long streaks who write long reviews, are leaving for apps that feel like *learning*, not a game.

- **Churn reasons:** among reviews saying the user has left or is about to leave, 43% cite monetization pressure (energy, subscription), 22% streak pressure, 18% reward clutter / UI changes, and 13% learning effectiveness.
- **Trend:** from July to November 2026, streak complaints grew 2.1× and reward-clutter complaints 2.4× as a share of negative reviews. Release 6.106 (Nov 16) has the highest 1-star rate of the last 23 releases (7.0%).
- **Destinations:** users who switch go to Babbel, Speak and Busuu. In the new apps they praise **grammar explanations, speaking practice, structure, and fewer interruptions**.

**Problem statement:** *Committed learners can't get a focused, explained, fair learning session in Duolingo's free experience. Engagement mechanics now interrupt the learning loop, so these users conclude the app no longer wants them to learn.*

## 2. Target users

**Primary: "the committed learner."**
- Free user with a streak of 30+ days who has studied at least 5 days a week for the past 4 weeks.
- Studies for a reason: travel, heritage, school, work.
- Wants to know *why* an answer is wrong.
- Tolerates gamification but resents interruptions and paywalls in the middle of a lesson.

**Secondary:** returning learners who lapsed after a streak loss.

**Not targeted:** casual learners who enjoy the game layer. Focus Mode is opt-in and changes nothing for them.

## 3. Goals and non-goals

**Goals**
1. Reduce churn among committed free learners.
2. Restore trust in the streak and in fairness ("I did my lesson, why did I lose my freeze?").
3. Close the explanation gap that pulls learners to Babbel and Busuu.

**Non-goals**
- Removing energy or the Super paywall for everyone. Monetization stays; this changes *where* it bites.
- A new course format or AI tutor. That's separate work, and AI content quality is itself a complaint.

## 4. Solution

An opt-in **Focus Mode** setting, offered in-context to users who match the target definition (e.g., after a 30-day streak milestone). It has four parts, in priority order.

| # | Component | What changes | Addresses (evidence) |
|---|---|---|---|
| P0 | **Quiet rewards** | Chests, puzzle pieces and celebration animations collapse into one end-of-session summary card. XP and gems are still awarded, with no extra taps. | Reward clutter / UI: 13.7% of Nov negative reviews, 18% of churn reasons |
| P0 | **Streak you can trust** | A freeze is used only when no lesson is recorded across *all* devices for the local day. Users see the lesson that counted ("Streak safe: lesson at 23:41 on web"). Failures are logged as incidents. | Streak complaints 2.1× since July; "freeze used even though I did my lesson" |
| P1 | **Free "why?" explanations** | 3 free grammar explanations per day on mistakes, plus a short tip card at the start of each unit. Super removes the daily cap. | #1 pull factor toward Babbel/Busuu (grammar explanations); learning-effectiveness complaints |
| P1 | **Practice doesn't cost energy** | Review and practice sessions on *completed* material are energy-free. New lessons still use energy. | Energy is the most-cited monetization grievance; "you can no longer review for lives" |

**Out of scope for v1:** ad changes (handled by the ads team), and per-language content corrections (handled by the content QA backlog fed by this analysis).

### User flow (P0)
1. The user hits a 30-day streak and sees a card: "Want a calmer lesson? Try Focus Mode."
2. They toggle it on. They can turn it off anytime in Settings → Lessons.
3. Lesson → single summary card → next lesson. Rewards are credited automatically.
4. At midnight local time, the streak check reads lesson events from every device before it touches a freeze.

## 5. Success metrics

| Type | Metric | Target |
|---|---|---|
| **Primary** | D30 retention of eligible committed learners (still active on day 30 after assignment) | +1.0 pp |
| Secondary | Lessons completed per active day | ≥ 0 (no drop) |
| Secondary | Streak-freeze support tickets / "freeze used wrongly" reports | −50% |
| Secondary | Share of new Play reviews tagged *churn-intent* (same LLM pipeline, weekly) | downward trend |
| Secondary | Explanation views per user and day-7 accuracy on explained items | descriptive |
| **Guardrail** | Super conversion rate among eligible users | no drop > 0.2 pp |
| **Guardrail** | Revenue per DAU (eligible segment) | no drop > 2% |
| **Guardrail** | Ad impressions per DAU | no drop > 5% |

## 6. Experiment plan

- **Design:** user-level randomized A/B among eligible users. Control keeps the current experience; treatment *offers* Focus Mode (intent-to-treat: the offer is the treatment, whether or not the user opts in). A third arm tests **P0 only** vs **P0+P1**, so the explanation and energy changes can be read separately from the quiet-UI change.
- **Sample size:**
  - Assume baseline D30 retention of 70% for this segment (to be replaced with the real number).
  - With MDE +1.0 pp, α = 0.05 and power 0.8 (two-sided), that needs about **32,700 users per arm**.
  - This is a small share of Duolingo's committed-learner base, so a 4-week enrollment plus a 30-day readout is realistic.
- **Duration:** 2 weeks of enrollment, then a 30-day follow-up per user. Don't read results before day 30.
- **Analysis:**
  - Difference in D30 retention, with a CUPED adjustment on pre-period activity.
  - Heterogeneity by streak length (30–99 / 100–364 / 365+).
  - Report the opt-in rate and the treatment-on-treated estimate separately.
- **Decision rule:**
  - Ship if the primary metric is significant and no guardrail is breached.
  - If P0 alone wins and P0+P1 hurts revenue, ship P0 and iterate on the explanation cap.
- **Risks:**
  - Novelty effect → keep 30-day readout.
  - Cannibalizing Super → guardrail + cap on free explanations.
  - Engineering cost of cross-device streak checks → ship the P0 streak fix behind its own flag first, since it's also a bug fix.

## 7. Open questions

1. What is the true D30 baseline and size of the committed-learner segment? Both change the sample size.
2. Should Focus Mode be offered proactively or only discoverable in Settings? Proactive offers raise adoption but could look like an admission that the default is noisy.
3. Can explanations be human-reviewed for the top 5 courses at launch, to avoid repeating the "AI-generated errors" complaint?

## 8. Launch checklist (abridged)

- [ ] Streak-check incident logging live (pre-req)
- [ ] Experiment config + guardrail alerts
- [ ] Review-tagging pipeline (this repo) scheduled weekly as a qualitative monitor
- [ ] Support macro for "freeze used wrongly"
