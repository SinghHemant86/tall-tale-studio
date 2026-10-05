"""Narration + per-character dialogue with Edge-TTS (free Microsoft neural voices).

Useful voices: en-IN-PrabhatNeural, en-IN-NeerjaNeural, hi-IN-MadhurNeural, hi-IN-SwaraNeural,
en-US-GuyNeural, en-GB-RyanNeural. List all with:  edge-tts --list-voices
"""
import asyncio
from pathlib import Path

from .common import duration, log, retry, run


def _edge(text: str, voice: str, rate: str, pitch: str, out: Path) -> None:
    import edge_tts

    async def go():
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(out))

    retry(lambda: asyncio.run(go()))


def _placeholder(text: str, out: Path) -> None:
    """Offline stand-in: a soft tone lasting roughly as long as the line would take to speak."""
    secs = max(1.5, len(text.split()) / 2.6)
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=180:duration={secs:.2f}",
         "-af", "volume=0.15", str(out)])


import re

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
# English voice -> matching Hindi voice when a line is written in Hindi (Devanagari)
HINDI_TWIN = {"en-IN-PrabhatNeural": "hi-IN-MadhurNeural", "en-IN-NeerjaNeural": "hi-IN-SwaraNeural"}


def voice_for_text(voice: str, text: str) -> str:
    """Hindi lines must be spoken by a Hindi voice, English lines by an English one."""
    is_hindi = bool(DEVANAGARI.search(text))
    if is_hindi and not voice.startswith("hi-"):
        return HINDI_TWIN.get(voice, "hi-IN-MadhurNeural" if "Prabhat" in voice or "Male" in voice else "hi-IN-SwaraNeural")
    if not is_hindi and voice.startswith("hi-"):
        rev = {v: k for k, v in HINDI_TWIN.items()}
        return rev.get(voice, voice)       # Hindi voices read Roman-script English reasonably; keep if unknown
    return voice


def speak_all(bible: dict, work: Path, cfg: dict, genre: dict | None = None) -> dict[str, list[tuple[Path, float, str]]]:
    """Returns {scene_id: [(audio_path, seconds, text), ...]}."""
    vcfg = cfg["voice"]
    chars = {c["id"]: c for c in bible["characters"]}
    d = work / "voice"
    d.mkdir(parents=True, exist_ok=True)
    result = {}
    for s in bible["scenes"]:
        clips = []
        for j, ln in enumerate(s["lines"]):
            out = d / f"{s['id']}_{j:02d}.mp3"
            if not out.exists():
                if ln["speaker"] == "narrator":
                    g = genre or {}
                    voice = bible.get("narrator_voice", vcfg["narrator"])
                    rate = g.get("narrator_rate", vcfg["narrator_rate"])
                    pitch = g.get("narrator_pitch", vcfg["narrator_pitch"])
                else:
                    c = chars[ln["speaker"]]
                    voice, rate, pitch = c["voice"], c.get("rate", "+0%"), c.get("pitch", "+0Hz")
                voice = voice_for_text(voice, ln["text"])
                log(f"  voice: {s['id']} line {j} ({ln['speaker']}, {voice})")
                if vcfg["engine"] == "edge":
                    _edge(ln["text"], voice, rate, pitch, out)
                else:
                    _placeholder(ln["text"], out)
            clips.append((out, duration(out), ln["text"]))
        result[s["id"]] = clips
    return result
