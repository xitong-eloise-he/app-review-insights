"""Scrape Google Play reviews (newest first) for Duolingo and competitors."""
import json, sys, time, pathlib
from google_play_scraper import reviews, Sort, app

APPS = {
    "duolingo": ("com.duolingo", 150000),
    "babbel":   ("com.babbel.mobile.android.en", 6000),
    "busuu":    ("com.busuu.android.enc", 6000),
    "memrise":  ("com.memrise.android.memrisecompanion", 6000),
    "speak":    ("com.selabs.speak", 6000),
}
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

def scrape(name, pkg, n):
    rows, token = [], None
    while len(rows) < n:
        batch, token = reviews(pkg, lang="en", country="us", sort=Sort.NEWEST,
                               count=min(200, n - len(rows)), continuation_token=token)
        if not batch:
            break
        rows += batch
        if token is None or token.token is None:
            break
        time.sleep(0.3)
    meta = app(pkg, lang="en", country="us")
    keep = ["reviewId", "content", "score", "thumbsUpCount", "reviewCreatedVersion", "at", "appVersion"]
    out = [{k: (str(r[k]) if k == "at" else r.get(k)) for k in keep} for r in rows]
    (OUT / f"{name}.json").write_text(json.dumps({"app": name, "package": pkg,
        "rating": meta.get("score"), "installs": meta.get("installs"), "reviews": out}))
    print(name, len(out), out[-1]["at"] if out else None, flush=True)

if __name__ == "__main__":
    for name in (sys.argv[1:] or APPS):
        scrape(name, *APPS[name])
