"""Transcribe an audio file in the repo with Whisper (CPU): python scripts/transcribe.py <path>"""
import sys
from pathlib import Path

from faster_whisper import WhisperModel

src = Path(sys.argv[1])
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = model.transcribe(str(src), vad_filter=True, beam_size=1)
lines = [f"[{int(s.start) // 60}:{int(s.start) % 60:02d}-{int(s.end) // 60}:{int(s.end) % 60:02d}] {s.text.strip()}"
         for s in segs]
(src.parent / "transcript.txt").write_text(
    f"language: {info.language} ({info.language_probability:.2f})\n" + "\n".join(lines), encoding="utf-8")
print(len(lines), "segments")
