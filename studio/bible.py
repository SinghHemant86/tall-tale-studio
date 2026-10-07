"""Story bible: load, validate and pick from the queue."""
import json
from pathlib import Path

from .common import ROOT

QUEUE = ROOT / "queue"
DONE = ROOT / "done"


class BibleError(ValueError):
    pass


def validate(b: dict) -> dict:
    for key in ("id", "title", "characters", "scenes"):
        if key not in b:
            raise BibleError(f"missing '{key}'")
    char_ids = {c["id"] for c in b["characters"]}
    for c in b["characters"]:
        for k in ("id", "name", "look", "voice"):
            if k not in c:
                raise BibleError(f"character missing '{k}': {c}")
    if not b["scenes"]:
        raise BibleError("no scenes")
    import re
    dev = re.compile(r"[\u0900-\u097F]")
    latin_words = re.compile(r"[A-Za-z]{2,}")
    from .genres import language
    hindi = language(b) == "hi"
    # Everything written is English (title, description, tags, hashtags, subtitles); only the audio is
    # Hindi, and the thumbnail text may be either.
    yt = b.get("youtube") or {}
    written = [("title", b["title"]), ("description", yt.get("description", ""))]
    written += [("tag", t) for t in yt.get("tags", [])] + [("hashtag", h) for h in yt.get("hashtags", [])]
    for what, val in written:
        if dev.search(val or ""):
            raise BibleError(f"{what} must be in English (\"{val[:60]}\"); only the audio is Hindi")
    for s in b["scenes"]:
        for ln in s["lines"]:
            txt = ln["text"]
            if hindi and latin_words.search(txt):
                raise BibleError(f"scene {s['id']}: Hindi story, but this line has English/Roman letters "
                                 f"(\"{txt[:60]}\"). Write every line in Devanagari (names and loanwords too).")
            if hindi and not (ln.get("en") or "").strip():
                raise BibleError(f"scene {s['id']}: Hindi line needs an \"en\" translation for the English "
                                 f"subtitles (\"{txt[:60]}\")")
            if dev.search(ln.get("en") or ""):
                raise BibleError(f"scene {s['id']}: \"en\" subtitle must be English (\"{ln['en'][:60]}\")")
            if dev.search(txt) and len(latin_words.findall(txt)) >= 3:
                raise BibleError(f"scene {s['id']}: line mixes Hindi and English (\"{txt[:60]}\"). "
                                 "Write each line in ONE language and never repeat it as a translation.")
            if len(txt.split()) > 40:
                raise BibleError(f"scene {s['id']}: line too long ({len(txt.split())} words); split it "
                                 "so the picture can change every few seconds.")
    scene_ids = {s["id"] for s in b["scenes"]}
    for i, sh in enumerate(b.get("shorts") or []):
        bad = [x for x in sh.get("scenes", []) if x not in scene_ids]
        if not sh.get("scenes") or bad:
            raise BibleError(f"short {i + 1}: needs 'scenes' from this story (unknown: {bad})")
        if dev.search(sh.get("title", "")):
            raise BibleError(f"short {i + 1}: title must be English")
    from .genres import GENRES
    genre = b.get("genre", "horror")
    if genre not in GENRES:
        raise BibleError(f"unknown genre '{genre}'. Use one of: {', '.join(GENRES)}")
    if GENRES[genre].get("true_story"):
        src = [s for s in b.get("sources", []) if str(s).startswith("http")]
        if not src:
            raise BibleError("true_incident stories need a 'sources' list of links (news, court records, archives)")
    for s in b["scenes"]:
        if "setting" not in s or not s.get("lines"):
            raise BibleError(f"scene {s.get('id')} needs 'setting' and 'lines'")
        for cid in s.get("characters", []):
            if cid not in char_ids:
                raise BibleError(f"scene {s['id']} references unknown character '{cid}'")
        for ln in s["lines"]:
            if ln["speaker"] != "narrator" and ln["speaker"] not in char_ids:
                raise BibleError(f"scene {s['id']}: unknown speaker '{ln['speaker']}'")
    return b


def load(path: Path) -> dict:
    return validate(json.loads(path.read_text(encoding="utf-8")))


def next_in_queue() -> Path | None:
    """Priority stories first ("go"), then alphabetical order."""
    items = sorted(p for p in QUEUE.glob("*.json"))
    if not items:
        return None
    prio = [p for p in items if json.loads(p.read_text(encoding="utf-8")).get("priority")]
    return (prio or items)[0]


def mark_done(path: Path, result: dict) -> Path:
    DONE.mkdir(exist_ok=True)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["result"] = result
    out = DONE / path.name
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    path.unlink()
    (QUEUE / "PROGRESS.md").unlink(missing_ok=True)
    return out
