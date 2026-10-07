"""Niche research: what is being watched in Hindi horror / true crime right now.

Runs on GitHub Actions (YouTube is reachable there). Public listings only, no login.
1. Searches YouTube for each query (top results by relevance and by this-month uploads).
2. Collects every channel that shows up, then each channel's latest videos with view counts.
3. Writes research/collected.json (for the yt-viral swipe tool) and research/search.json.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

QUERIES = [
    "hindi horror story", "real horror story hindi", "sacchi bhoot ki kahani", "bhootiya kahani",
    "horror podcast hindi", "haunted place india", "true crime hindi", "crime story hindi real",
    "psychological thriller story hindi", "dark story hindi", "real ghost experience india",
    "horror story in hindi animated", "unsolved mystery india hindi", "village horror story hindi",
]
PER_QUERY = 30
CHANNELS_MAX = 45
PER_CHANNEL = 40
OUT = Path(__file__).resolve().parent.parent / "research"


def ytdlp(*args) -> dict:
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--ignore-errors", "--no-warnings", *args],
                       capture_output=True, text=True, timeout=300)
    try:
        return json.loads(r.stdout or "{}")
    except ValueError:
        print("  yt-dlp failed:", r.stderr[-300:], file=sys.stderr)
        return {}


def main():
    OUT.mkdir(exist_ok=True)
    search, chan_hits = [], Counter()
    names = {}
    for q in QUERIES:
        for label, url in (("relevance", f"ytsearch{PER_QUERY}:{q}"),
                           ("this_month", f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}&sp=EgIIBA%3D%3D")):
            data = ytdlp("--playlist-end", str(PER_QUERY), url)
            for e in data.get("entries") or []:
                cid = e.get("channel_id")
                row = {"query": q, "sort": label, "title": e.get("title"), "views": e.get("view_count"),
                       "duration": e.get("duration"), "channel": e.get("channel") or e.get("uploader"),
                       "channel_id": cid, "url": e.get("url")}
                search.append(row)
                if cid:
                    chan_hits[cid] += 1
                    names[cid] = row["channel"]
        print(f"searched: {q}")
    (OUT / "search.json").write_text(json.dumps(search, indent=1, ensure_ascii=False))

    collected = []
    for cid, hits in chan_hits.most_common(CHANNELS_MAX):
        data = ytdlp("--playlist-end", str(PER_CHANNEL), f"https://www.youtube.com/channel/{cid}/videos")
        n = 0
        for e in data.get("entries") or []:
            if e.get("view_count") is None:
                continue
            collected.append({"channel": names.get(cid) or data.get("channel") or cid, "channel_id": cid,
                              "title": e.get("title"), "views": e.get("view_count"),
                              "duration": e.get("duration"), "url": e.get("url"),
                              "subscribers": data.get("channel_follower_count")})
            n += 1
        print(f"channel {names.get(cid)}: {n} videos ({hits} search hits)")
    (OUT / "collected.json").write_text(json.dumps(collected, indent=1, ensure_ascii=False))
    print(f"done: {len(search)} search rows, {len(collected)} channel videos")


if __name__ == "__main__":
    main()
