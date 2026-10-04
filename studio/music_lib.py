"""Music library: understands tracks by their names and by measuring them.

Names: Pixabay filenames already say what a track is ("dark-horror-opener", "scary-music-box"),
so keywords in the name decide its role: intro, outro, calm, dread or chase.

Measurement: each track is decoded and its loudness measured every half second. That gives an
intensity curve, so a calm scene gets the quietest stretch of a track, a chase scene the loudest,
and the sharp hits (sudden jumps in loudness) are found so they can land on a scene's key moment.
Results are cached in music/library.json and refreshed when files change.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

from .common import ROOT, log

AUDIO = (".mp3", ".wav", ".ogg", ".m4a")
STEP = 0.5  # seconds per loudness measurement

# filename keyword -> role. First match wins, so specific words come first.
ROLE_WORDS = [
    ("intro", ["opener", "opening", "intro", "logo", "title"]),
    ("outro", ["outro", "ending", "credits", "pad", "closing"]),
    ("calm", ["music-box", "musicbox", "lullaby", "piano", "calm", "soft", "sad"]),
    ("chase", ["trailer", "chase", "action", "pulse", "heartbeat", "tension", "tense", "run"]),
    ("dread", ["atmosphere", "ambience", "ambient", "background", "soundscape", "drone",
               "suspense", "eerie", "whisper", "breath", "dissonant", "dark", "mystery", "pad"]),
]

# scene mood -> (preferred role, target intensity percentile within the track)
MOOD_TARGET = {
    "intro": ("intro", 60), "outro": ("outro", 40),
    "calm": ("calm", 20), "piano": ("calm", 30), "ambient": ("dread", 25),
    "dread": ("dread", 45), "drone": ("dread", 50),
    "pulse": ("chase", 70), "chase": ("chase", 85), "reveal": ("chase", 95),
}


def role_of(name: str) -> str:
    n = name.lower().replace("_", "-")
    for role, words in ROLE_WORDS:
        if any(w in n for w in words):
            return role
    return "dread"


def _loudness(path: Path) -> list[float]:
    """Loudness in dB every STEP seconds (mono, 8 kHz decode is plenty for this)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "8000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = int(8000 * STEP)
    frames = x[: len(x) // n * n].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-10)
    return [round(float(v), 1) for v in 20 * np.log10(rms)]


def _hits(curve: list[float]) -> list[float]:
    """Seconds where loudness jumps 8+ dB above the previous two seconds: impacts and stingers."""
    c = np.array(curve)
    hits = []
    for i in range(4, len(c)):
        if c[i] - c[i - 4:i].mean() >= 8 and c[i] > np.percentile(c, 60):
            if not hits or i * STEP - hits[-1] > 3:
                hits.append(round(i * STEP, 1))
    return hits


def build(folder: Path | None = None) -> dict:
    folder = folder or ROOT / "music"
    cache_path = folder / "library.json"
    try:
        cache = json.loads(cache_path.read_text())
    except (OSError, ValueError):
        cache = {}
    lib, changed = {}, False
    for p in sorted(folder.rglob("*")):
        if p.suffix.lower() not in AUDIO:
            continue
        key = p.relative_to(folder).as_posix()
        stamp = f"{p.stat().st_size}"
        if cache.get(key, {}).get("stamp") == stamp:
            lib[key] = cache[key]
            continue
        curve = _loudness(p)
        c = np.array(curve)
        lib[key] = {
            "stamp": stamp,
            "folder": p.parent.name if p.parent != folder else "",
            "role": role_of(p.name),
            "seconds": round(len(curve) * STEP, 1),
            "level_db": round(float(np.median(c)), 1),
            "dynamics_db": round(float(np.percentile(c, 90) - np.percentile(c, 10)), 1),
            "hits": _hits(curve),
            "curve": curve,
        }
        changed = True
        log(f"  music: analysed {key} -> {lib[key]['role']}, {lib[key]['seconds']}s, "
            f"{len(lib[key]['hits'])} hits")
    if changed or set(lib) != set(cache):
        try:
            cache_path.write_text(json.dumps(lib, indent=1))
        except OSError:
            pass
    return lib


def choose(lib: dict, genre: str, mood: str, seconds: float, index: int) -> tuple[Path, float] | None:
    """Pick a track and a start offset for one segment of the video."""
    role, pct = MOOD_TARGET.get(mood, ("dread", 50))
    items = list(lib.items())
    if not items:
        return None

    def pool(pred):
        return [(k, v) for k, v in items if pred(k, v)]

    in_genre = lambda k, v: v["folder"] == genre  # noqa: E731
    candidates = (
        pool(lambda k, v: v["folder"] == mood)                          # music/intro/, music/outro/
        or pool(lambda k, v: in_genre(k, v) and v["role"] == role)      # right genre, right role
        or ([] if role in ("intro", "outro") else pool(lambda k, v: in_genre(k, v) and v["role"] != "intro"))
        or pool(lambda k, v: v["role"] == role)                          # right role, any genre
        or pool(lambda k, v: v["role"] not in ("intro", "outro"))
        or items
    )
    key, info = candidates[index % len(candidates)]
    path = ROOT / "music" / key
    choose.last_level = info["level_db"]

    # intro: start so the track's first big hit lands 60% into the card (the logo reveal)
    if role == "intro":
        hits = [h for h in info["hits"] if h >= seconds * 0.6]
        return path, round(max(0.0, hits[0] - seconds * 0.6), 1) if hits else 0.0
    if role == "outro" or info["seconds"] <= seconds + 1:
        return path, 0.0
    c = np.array(info["curve"])
    win = max(1, int(seconds / STEP))
    target = np.percentile(c, pct)
    means = np.convolve(c, np.ones(win) / win, mode="valid")
    best = int(np.argmin(np.abs(means - target)))
    return path, round(best * STEP, 1)


def describe(lib: dict) -> str:
    rows = [f"{k}: {v['role']}, {v['seconds']}s, level {v['level_db']} dB, "
            f"range {v['dynamics_db']} dB, hits at {v['hits'] or 'none'}" for k, v in lib.items()]
    return "\n".join(rows)


if __name__ == "__main__":
    print(describe(build()))
