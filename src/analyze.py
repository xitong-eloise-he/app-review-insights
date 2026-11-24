"""Aggregate reviews + LLM labels into report/data.json.

Without labels (data/labels.jsonl) it still produces rating trends, version drops and keyword trends.
"""
import json, pathlib, re
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
df = pd.read_parquet(ROOT / "data/reviews.parquet")
duo = df[df.app == "duolingo"].copy()
duo["week"] = duo["at"].dt.to_period("W-SUN").dt.start_time.dt.strftime("%Y-%m-%d")
duo["month"] = duo["at"].dt.to_period("M").astype(str)
out = {}

# --- overview per app
out["apps"] = (df.groupby("app").agg(reviews=("id", "size"), avg_stars=("score", "mean"),
              one_star=("score", lambda s: (s == 1).mean()), first=("at", "min"), last=("at", "max"))
              .reset_index().assign(first=lambda d: d["first"].dt.strftime("%Y-%m-%d"),
                                    last=lambda d: d["last"].dt.strftime("%Y-%m-%d")).to_dict("records"))

# --- weekly rating trend (drop the partial last week)
wk = duo.groupby("week").agg(n=("id", "size"), avg=("score", "mean"), one=("score", lambda s: (s == 1).mean())).reset_index()
out["weekly"] = wk.iloc[:-1].round(4).to_dict("records")

# --- version-level ratings: versions with >= 300 reviews, in release order
v = duo.dropna(subset=["version"]).copy()
v["vkey"] = v["version"].str.extract(r"^(\d+\.\d+)")[0]
vs = (v.groupby("vkey").agg(n=("id", "size"), avg=("score", "mean"), one=("score", lambda s: (s == 1).mean()),
                            first_seen=("at", "min")).reset_index())
vs = vs[vs.n >= 300].copy()
vs["order"] = vs.vkey.str.split(".").apply(lambda p: (int(p[0]), int(p[1])))
vs = vs.sort_values("order").drop(columns="order")
vs["delta_vs_prev3"] = vs["avg"] - vs["avg"].shift(1).rolling(3, min_periods=1).mean()
vs["first_seen"] = vs["first_seen"].dt.strftime("%Y-%m-%d")
out["versions"] = vs.round(4).to_dict("records")

# --- keyword trends (share of reviews per month mentioning a theme), all reviews, no LLM
THEMES = {
    "energy / hearts": r"\benergy\b|\bhearts?\b",
    "ads": r"\bads?\b|advert",
    "Super / Max / price": r"\bsuper\b|\bmax\b|subscription|paywall|price|expensive|pay\b",
    "AI": r"\bai\b|artificial intelligence|chatgpt",
    "streak": r"\bstreak",
    "bug / crash": r"crash|bug|freez|glitch|not working|won'?t load",
}
duo_l = duo.content.str.lower()
kt = []
for name, pat in THEMES.items():
    hit = duo_l.str.contains(pat, regex=True)
    g = duo.assign(hit=hit).groupby("month").agg(share=("hit", "mean"), stars_when_mentioned=("score", lambda s: s[hit.loc[s.index]].mean()))
    for m, r in g.iterrows():
        kt.append({"theme": name, "month": m, "share": round(r.share, 4), "stars": round(r.stars_when_mentioned, 2)})
out["keyword_trends"] = kt

# --- LLM labels
lab_path = ROOT / "data/labels.jsonl"
if lab_path.exists():
    lab = pd.DataFrame([json.loads(l) for l in open(lab_path)])
    w = pd.read_csv(ROOT / "data/sample_weights.csv")
    L = lab.merge(w, on="id").merge(df[["id", "score", "at", "version", "content", "thumbsUpCount"]], on="id")
    L["month"] = L["at"].dt.to_period("M").astype(str)
    out["n_labeled"] = len(L)
    D = L[L.app == "duolingo"]
    ex = D.explode("pain_points")
    ex = ex[~ex.pain_points.isin(["none"])]
    # weighted share of all Duolingo reviews raising each pain point
    tot_w = D.weight.sum()
    pp = (ex.groupby("pain_points").agg(w=("weight", "sum"), n=("id", "nunique"), stars=("score", "mean"))
            .assign(share=lambda d: d.w / tot_w).sort_values("share", ascending=False).reset_index())
    out["pain_points"] = pp.drop(columns="w").round(4).to_dict("records")
    # pain points among 1-star reviews only
    one = D[D.score == 1]; ex1 = one.explode("pain_points")
    out["pain_points_1star"] = (ex1.groupby("pain_points").weight.sum() / one.weight.sum()).round(4).sort_values(ascending=False).to_dict()
    # monthly trend of top pain points (weighted)
    mt = []
    for m, g in D.groupby("month"):
        e = g.explode("pain_points"); tw = g.weight.sum()
        for p, s in (e.groupby("pain_points").weight.sum() / tw).items():
            mt.append({"month": m, "pain_point": p, "share": round(s, 4)})
    out["pain_trend"] = mt
    # sentiment by month
    out["sentiment"] = (D.groupby(["month", "sentiment"]).weight.sum() / D.groupby("month").weight.sum()).round(4).reset_index(name="share").to_dict("records")
    # switching
    sw = D[D.switching.isin(["switched_away", "considering"])]
    out["churn_signal_share"] = round(sw.weight.sum() / tot_w, 4)
    exs = sw.explode("pain_points")
    out["churn_reasons"] = (exs.groupby("pain_points").weight.sum() / sw.weight.sum()).round(4).sort_values(ascending=False).to_dict()
    out["competitors_named_by_duo_users"] = D.competitor_mentioned.dropna().str.strip().str.title().value_counts().head(10).to_dict()
    C = L[(L.app != "duolingo")]
    came = C[C.switching == "switched_from_duolingo"]
    out["switchers_from_duolingo"] = {"n": len(came), "by_app": came.app.value_counts().to_dict(),
        "avg_stars_given_to_new_app": round(came.score.mean(), 2) if len(came) else None}
    # what switchers praise in the new app / blame on Duolingo: features they mention
    out["switcher_features"] = came.explode("features").features.dropna().str.lower().value_counts().head(15).to_dict()
    out["switcher_quotes"] = came.sort_values("thumbsUpCount", ascending=False).head(8)[["app", "score", "content"]].assign(
        content=lambda d: d.content.str.slice(0, 280)).to_dict("records")
    # most-liked complaint quotes per top pain point
    q = {}
    for p in pp.pain_points.head(6):
        s = ex[(ex.pain_points == p) & (ex.score <= 2)].sort_values("thumbsUpCount", ascending=False).head(3)
        q[p] = s[["score", "thumbsUpCount", "content"]].assign(content=lambda d: d.content.str.slice(0, 260)).to_dict("records")
    out["quotes"] = q
    # features mentioned most in negative Duolingo reviews
    out["neg_features"] = D[D.sentiment == "negative"].explode("features").features.dropna().str.lower().value_counts().head(15).to_dict()

(ROOT / "report").mkdir(exist_ok=True)
(ROOT / "report/data.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: (v if not isinstance(v, list) else f"{len(v)} rows") for k, v in out.items() if k not in ("quotes", "switcher_quotes")}, indent=1, default=str)[:4000])

# --- extra cuts used in the report
if lab_path.exists():
    # competitor pain points from their own random reviews (what's wrong with the alternatives)
    R = L[(L.app != "duolingo") & (L.stratum == "random")]
    comp_pp = {}
    for a, g in R.groupby("app"):
        e = g.explode("pain_points")
        comp_pp[a] = (e.groupby("pain_points").size() / len(g)).round(3).sort_values(ascending=False).head(5).to_dict()
    out["competitor_pain_points"] = comp_pp
    out["competitor_sentiment"] = (R.groupby("app").sentiment.value_counts(normalize=True).round(3).unstack().fillna(0).to_dict("index"))
    # negative Duolingo reviews: pain-point mix by release group
    D = D.copy()
    D["v"] = D.version.str.extract(r"^(\d+\.\d+)")[0]
    D["release"] = D.v.map(lambda x: "6.106 (Nov 16)" if x == "6.106" else
                           ("6.102–6.105 (Oct 19–Nov 15)" if x in ("6.102", "6.103", "6.104", "6.105") else "≤ 6.101 (Jul–Oct 18)"))
    neg = D[D.score <= 2]
    e = neg.explode("pain_points")
    mix = (e.groupby(["release", "pain_points"]).weight.sum() / neg.groupby("release").weight.sum()).round(4)
    out["release_mix"] = mix.reset_index(name="share").to_dict("records")
    out["release_neg_n"] = neg.groupby("release").size().to_dict()
    # monthly share of negative reviews that cite streak / monetization
    nm = []
    for m, g in neg.groupby("month"):
        e2 = g.explode("pain_points"); tw = g.weight.sum()
        for p in ["streak_gamification", "monetization_paywall", "ui_redesign", "bugs_performance", "energy_hearts_limits", "ai_features"]:
            nm.append({"month": m, "pain_point": p, "share": round(e2[e2.pain_points == p].weight.sum() / tw, 4)})
    out["neg_month_mix"] = nm
    (ROOT / "report/data.json").write_text(json.dumps(out, indent=1, default=str))
