"""Vertical Shorts / Reels cut from the finished long video.

The story marks its Short moments ("shorts": [{"scenes": [...], "title": "..."}]). Each one is taken
from the long video's own timeline (same voices, music and images, so no extra credits), turned into
1080x1920: the shot sits in the middle over a blurred copy of itself, the title on top, big English
subtitles below, the logo in the corner, and a closing line pointing to the full story.
"""
from pathlib import Path

from .common import ROOT, log, run

W, H = 1080, 1920
MAX_SEC = 58.0
END_SEC = 2.5
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _srt_time(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


def _ass_time(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def windows(story: dict, scene_times: dict, subs: list) -> list[dict]:
    """Start/end seconds of each marked Short in the long video, trimmed to fit under a minute."""
    out = []
    for i, sh in enumerate(story.get("shorts") or []):
        ids = [s for s in sh.get("scenes", []) if s in scene_times]
        if not ids:
            log(f"  short {i + 1}: none of its scenes {sh.get('scenes')} exist, skipped")
            continue
        a = min(scene_times[s][0] for s in ids)
        b = max(scene_times[s][1] for s in ids)
        if b - a > MAX_SEC - END_SEC:
            # cut at the end of the last subtitle line that still fits, never mid-sentence
            ends = [e for (s, e, _) in subs if a < e <= a + MAX_SEC - END_SEC]
            b = (max(ends) + 0.4) if ends else a + MAX_SEC - END_SEC
        out.append({"n": i + 1, "start": a, "end": b, "title": sh.get("title") or story["title"],
                    "scenes": ids})
    return out


def render(win: dict, joined: Path, final: Path, subs: list, work: Path, logo: Path) -> Path:
    d = work / "shorts"
    d.mkdir(parents=True, exist_ok=True)
    a, b = win["start"], win["end"]
    dur = b - a + END_SEC
    out = d / f"short_{win['n']:02d}.mp4"

    # subtitles for this window, shifted to start at 0 (written as ASS at full 1080x1920 so the
    # position is exact: centred, just under the picture)
    rows = [(max(0.0, s - a), min(b - a, e - a), t) for (s, e, t) in subs if e > a and s < b]
    title = d / f"short_{win['n']:02d}_title.txt"
    title.write_text(_wrap(win["title"].split("|")[0].strip(), 26), encoding="utf-8")
    endtxt = d / "end.txt"
    endtxt.write_text("Watch the full story\non Tall-Tale", encoding="utf-8")

    fg_h = 810                                    # the shot cropped to 4:3 so it fills more of the phone
    fg_y = 400
    sub_top = fg_y + fg_h + 50                    # subtitles start just under the picture
    ass = d / f"short_{win['n']:02d}.ass"
    ass.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n"
        f"Style: S,DejaVu Sans,66,&H00F0F0F0,&H00F0F0F0,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,8,70,70,{sub_top},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        + "".join(f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},S,,0,0,0,,{t.replace(chr(10), ' ')}\n" for s, e, t in rows),
        encoding="utf-8")
    fc = (
        f"[0:v]split=2[a][b];"
        f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,"
        f"eq=brightness=-0.12:saturation=0.8[bg];"
        f"[b]scale=-2:{fg_h},crop={W}:{fg_h}[fg];"
        f"[bg][fg]overlay=0:{fg_y}[v1];"
        f"[2:v]scale=150:150[lg];[v1][lg]overlay={W - 175}:40[v2];"
        f"[v2]drawtext=fontfile={FONT}:textfile='{title.as_posix()}':fontcolor=0xDEB96E:fontsize=58:"
        f"line_spacing=12:x=(w-text_w)/2:y={fg_y - 60}-text_h:borderw=4:bordercolor=black[v3];"
        f"[v3]ass='{ass.as_posix()}'[v4];"
        f"[v4]drawbox=x=0:y=0:w=iw:h=ih:color=black@0.6:t=fill:enable='gte(t,{dur - END_SEC:.2f})',"
        f"drawtext=fontfile={FONT}:textfile='{endtxt.as_posix()}':fontcolor=0xDEB96E:fontsize=72:"
        f"line_spacing=20:x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{dur - END_SEC:.2f})',"
        f"fade=t=in:st=0:d=0.2,format=yuv420p[v]"
    )
    run(["ffmpeg", "-y",
         "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(joined),
         "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(final),
         "-loop", "1", "-i", str(logo),
         "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
         "-af", f"afade=t=out:st={dur - 1.2:.2f}:d=1.2",
         "-t", f"{dur:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)])
    log(f"  short {win['n']}: {dur:.0f}s -> {out.name}")
    return out


def _wrap(text: str, width: int) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\n".join(lines[:3])


def make_all(story: dict, scene_times: dict, subs: list, work: Path) -> list[dict]:
    wins = windows(story, scene_times, subs)
    logo = ROOT / "assets" / "logo.png"
    for w in wins:
        w["file"] = render(w, work / "joined.mp4", work / f"{story['id']}.mp4", subs, work, logo)
    return wins
