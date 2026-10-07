"""Transcribe an audio file in the repo with Whisper (CPU): python scripts/transcribe.py <path>"""
import sys
from pathlib import Path

from faster_whisper import WhisperModel

import subprocess
import traceback

src = Path(sys.argv[1])
try:
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)  # decoded here: avoids PyAV version issues
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, info = model.transcribe(audio, vad_filter=True, beam_size=1)
    segs = list(segs)
except Exception as e:  # noqa: BLE001
    print("::error title=transcribe::" + (repr(e) + " " + traceback.format_exc().splitlines()[-1])[:400])
    raise
lines = [f"[{int(s.start) // 60}:{int(s.start) % 60:02d}-{int(s.end) // 60}:{int(s.end) % 60:02d}] {s.text.strip()}"
         for s in segs]
(src.parent / "transcript.txt").write_text(
    f"language: {info.language} ({info.language_probability:.2f})\n" + "\n".join(lines), encoding="utf-8")
print(len(lines), "segments")
