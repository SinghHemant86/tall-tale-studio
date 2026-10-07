"""Break a YouTube video down for review: metadata, contact sheets, cuts, loudness, transcript.

    python scripts/analyse_video.py <youtube url>
Writes research/analysis/<video id>/ . Public or unlisted videos only (no login is used).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

url = sys.argv[1]
vid = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url).group(1)
out = Path(__file__).resolve().parent.parent / "research" / "analysis" / vid
out.mkdir(parents=True, exist_ok=True)
work = Path("/tmp/analyse")
work.mkdir(exist_ok=True)
video = work / "v.mp4"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# 1) metadata + download (720p is plenty)
r = run(["yt-dlp", "-J", "--no-warnings", url])
if r.returncode != 0:
    msg = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "unknown"
    print(f"::error title=yt-dlp::{msg[:400]}")
    sys.exit(1)
meta = json.loads(r.stdout)
keep = {k: meta.get(k) for k in ("title", "description", "duration", "view_count", "like_count", "comment_count",
                                 "upload_date", "tags", "categories", "channel", "width", "height", "fps",
                                 "chapters", "language", "availability")}
(out / "meta.json").write_text(json.dumps(keep, indent=1, ensure_ascii=False))
r = run(["yt-dlp", "-f", "bv*[height<=720]+ba/b[height<=720]/b", "--merge-output-format", "mp4",
         "-o", str(video), "--no-warnings", url])
if not video.exists():
    print("::error title=download::" + r.stderr.strip().replace("\n", " ")[-400:])
    sys.exit(1)
dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]).stdout)
print(f"downloaded {dur:.0f}s")

# 2) contact sheets: one frame every STEP seconds, 5x4 grid per sheet, timestamped
STEP = 3 if dur <= 600 else 5
frames = work / "frames"
frames.mkdir(exist_ok=True)
run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps=1/{STEP},scale=320:-2", str(frames / "f%05d.jpg")])
files = sorted(frames.glob("f*.jpg"))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
per = 20
for s in range(0, len(files), per):
    chunk = files[s:s + per]
    w, h = Image.open(chunk[0]).size
    sheet = Image.new("RGB", (5 * w + 24, 4 * (h + 4) + 4), (10, 10, 10))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        x, y = 4 + (i % 5) * (w + 4), 4 + (i // 5) * (h + 4)
        sheet.paste(Image.open(f), (x, y))
        t = (s + i) * STEP
        d.text((x + 4, y + 4), f"{t // 60}:{t % 60:02d}", font=font, fill=(255, 220, 0), stroke_width=2,
               stroke_fill=(0, 0, 0))
    sheet.save(out / f"sheet_{s // per + 1:02d}.jpg", quality=80)

# 3) cuts (scene changes) and shot lengths
r = run(["ffmpeg", "-i", str(video), "-vf", "select='gt(scene,0.30)',showinfo", "-f", "null", "-"])
cuts = [round(float(m), 2) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]
shots = [b - a for a, b in zip([0.0] + cuts, cuts + [dur])]
stats = {"duration_s": round(dur, 1), "cuts": len(cuts), "avg_shot_s": round(sum(shots) / len(shots), 2),
         "longest_shots": sorted(((round(l, 1), round(a, 1)) for l, a in zip(shots, [0.0] + cuts)), reverse=True)[:10],
         "cut_times": cuts}

# 4) loudness per second (momentary LUFS) -> quiet stretches
r = run(["ffmpeg", "-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"])
lufs = {}
for m in re.finditer(r"t:\s*([\d.]+).*?M:\s*(-?[\d.]+)", r.stderr):
    lufs.setdefault(int(float(m.group(1))), float(m.group(2)))
il = re.search(r"Integrated loudness:\s+I:\s+(-?[\d.]+)", r.stderr)
stats["integrated_lufs"] = float(il.group(1)) if il else None
stats["loudness_per_10s"] = [round(sum(v for k, v in lufs.items() if s <= k < s + 10) /
                                   max(1, sum(1 for k in lufs if s <= k < s + 10)), 1)
                             for s in range(0, int(dur), 10)]
(out / "stats.json").write_text(json.dumps(stats, indent=1))

# 5) transcript with timestamps (Whisper on CPU)
from faster_whisper import WhisperModel  # noqa: E402

model = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = model.transcribe(str(video), vad_filter=True, beam_size=1)
lines = [f"[{int(s.start) // 60}:{int(s.start) % 60:02d}] {s.text.strip()}" for s in segs]
(out / "transcript.txt").write_text(f"language: {info.language} ({info.language_probability:.2f})\n" + "\n".join(lines),
                                    encoding="utf-8")
print("done:", out)
