"""Narration + per-character dialogue with Edge-TTS (free Microsoft neural voices).

Useful voices: en-IN-PrabhatNeural, en-IN-NeerjaNeural, hi-IN-MadhurNeural, hi-IN-SwaraNeural,
en-US-GuyNeural, en-GB-RyanNeural. List all with:  edge-tts --list-voices
"""
import asyncio
import os
from pathlib import Path

import requests

from .common import duration, log, retry, run

ELEVEN = "https://api.elevenlabs.io/v1"


def _eleven(text: str, voice_id: str, out: Path, ecfg: dict, settings: dict | None = None) -> None:
    key = os.environ["ELEVENLABS_API_KEY"].strip()
    vs = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}
    vs.update(ecfg.get("voice_settings") or {})
    vs.update(settings or {})

    def fetch():
        r = requests.post(f"{ELEVEN}/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                          headers={"xi-api-key": key, "accept": "audio/mpeg"},
                          json={"text": text, "model_id": ecfg.get("model", "eleven_multilingual_v2"),
                                "voice_settings": vs}, timeout=120)
        if r.status_code == 401:
            raise PermissionError(f"ElevenLabs rejected the key: {r.text[:200]}")
        if r.status_code >= 400:
            raise RuntimeError(f"ElevenLabs HTTP {r.status_code}: {r.text[:300]}")
        out.write_bytes(r.content)

    retry(fetch)


def eleven_available(bible: dict, ecfg: dict) -> bool:
    """True if a key is set and the month's remaining characters cover this whole story.
    Checking up front keeps one consistent voice set per video (no mid-story switch to Edge)."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        return False
    need = sum(len(ln["text"]) for s in bible["scenes"] for ln in s["lines"])
    try:
        r = requests.get(f"{ELEVEN}/user/subscription", headers={"xi-api-key": key}, timeout=30)
        r.raise_for_status()
        sub = r.json()
        left = sub["character_limit"] - sub["character_count"]
        log(f"  elevenlabs: {left:,} characters left this month, story needs {need:,}")
        return left >= need * 1.05
    except Exception as e:  # noqa: BLE001
        log(f"  elevenlabs: could not check quota ({e!s:.120}); trying anyway")
        return True


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
    ecfg = vcfg.get("elevenlabs") or {}
    engine = vcfg["engine"]
    if engine == "elevenlabs" and not eleven_available(bible, ecfg):
        log("  elevenlabs not available for this story -> using free Edge voices")
        engine = "edge"
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
                if engine == "elevenlabs":
                    if ln["speaker"] == "narrator":
                        vid = bible.get("narrator_eleven") or ecfg["narrator"]
                        settings = None
                    else:
                        c = chars[ln["speaker"]]
                        vid = c.get("eleven_voice") or ecfg.get("default_" + c.get("gender", "male"), ecfg["narrator"])
                        settings = c.get("eleven_settings")
                    log(f"    elevenlabs voice {vid}")
                    _eleven(ln["text"], vid, out, ecfg, settings)
                elif engine == "edge":
                    _edge(ln["text"], voice, rate, pitch, out)
                else:
                    _placeholder(ln["text"], out)
            clips.append((out, duration(out), ln["text"]))
        result[s["id"]] = clips
    return result
