"""Build the review table (all reviews) and the stratified sample sent to the LLM.

Sample design:
  * Duolingo: up to 250 reviews per (month, star bucket) cell, stars bucketed 1 / 2-3 / 4-5,
    so negative reviews and every month are represented. Weights in the sample let us re-project shares.
  * Competitors: every review that mentions Duolingo (switching signal) + 250 random others per app.
"""
import json, pathlib, random
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
random.seed(7)

frames = []
for f in sorted((ROOT / "data/raw").glob("*.json")):
    d = json.loads(f.read_text())
    df = pd.DataFrame(d["reviews"]); df["app"] = d["app"]; frames.append(df)
df = pd.concat(frames, ignore_index=True)
df = df.rename(columns={"reviewId": "id", "reviewCreatedVersion": "version"})
df["at"] = pd.to_datetime(df["at"])
df["content"] = df["content"].fillna("")
df = df.drop_duplicates("id")
df.to_parquet(ROOT / "data/reviews.parquet", index=False)

duo = df[(df.app == "duolingo") & (df.content.str.split().str.len() >= 4)].copy()
duo["month"] = duo["at"].dt.to_period("M").astype(str)
duo["bucket"] = pd.cut(duo.score, [0, 1, 3, 5], labels=["1", "2-3", "4-5"]).astype(str)
cell_n = duo.groupby(["month", "bucket"]).size()
parts = []
for (m, b), g in duo.groupby(["month", "bucket"]):
    s = g.sample(min(250, len(g)), random_state=7)
    s = s.assign(weight=len(g) / len(s))
    parts.append(s)
duo_s = pd.concat(parts)

comp = df[df.app != "duolingo"].copy()
mention = comp[comp.content.str.contains("duolingo|duo lingo|the owl", case=False, regex=True)]
rest = comp.drop(mention.index).groupby("app", group_keys=False).apply(lambda g: g.sample(min(250, len(g)), random_state=7))
comp_s = pd.concat([mention.assign(weight=1.0, stratum="mentions_duolingo"), rest.assign(weight=1.0, stratum="random")])

sample = pd.concat([duo_s.assign(stratum="duo_" + duo_s.bucket), comp_s], ignore_index=True)
with open(ROOT / "data/sample.jsonl", "w") as f:
    for r in sample.itertuples():
        f.write(json.dumps({"id": r.id, "app": r.app, "score": int(r.score), "content": r.content}) + "\n")
sample[["id", "app", "stratum", "weight"]].to_csv(ROOT / "data/sample_weights.csv", index=False)
print("all reviews:", len(df), df.groupby("app").size().to_dict())
print("duolingo date range:", duo["at"].min(), duo["at"].max())
print("sample:", len(sample), sample.groupby("stratum").size().to_dict())
