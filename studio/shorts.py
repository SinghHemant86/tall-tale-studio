"""Vertical Shorts / Reels, cut like a trailer from each long video.

The story marks its Short moments ("shorts": [{"scenes": [...], "title": "...", "hook": "..."}]).
The sound is the long video's own mix for that stretch (same voices and music: no extra voice
credits). The picture is new: a fresh square image every ~1.5 s made for the phone screen (tight
close-ups, eyes, hands, objects), each with a fast push-in or a shake, a white flash on some cuts,
an opening hook shot, captions that pop in three words at a time, and a closing card.
If the image engine runs out (daily quota), a shot falls back to a frame of the long video.
"""
import json
import math
from pathlib import Path

from . import images
from .common import ROOT, log, run

W, H = 1080, 1920
SQ = 1080                    # the picture is square, full width
SQ_Y = 380                   # its top edge
MAX_SEC = 58.0
END_SEC = 2.5
SHOT_SEC = 1.5               # a new picture this often
FPS = 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TRAILER_SHOTS = [
    "extreme close-up of {who} eyes, terrified, in {setting}",
    "close-up of a trembling hand in {setting}",
    "dramatic close-up of an object in {setting}, harsh light",
    "{who} seen from behind, standing still, {setting}",
    "dutch angle, {setting}, something moving in the shadows",
    "close-up of {who} face half in shadow, {setting}",
    "a dark doorway in {setting}, a pale shape inside",
    "low angle, {who} looking up in fear, {setting}",
]
STYLE_TAIL = "vertical composition, subject centred, cinematic, high contrast"
MOVES = [  # zoom, x, y (F = frames in the shot)
    ("1+0.22*on/F", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),                       # fast push-in
    ("1.25-0.20*on/F", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),                    # pull-out
    ("1.15", "iw/2-(iw/zoom/2)+12*sin(on*1.9)", "ih/2-(ih/zoom/2)+9*cos(on*2.3)"),  # shake
    ("1.12+0.10*on/F", "(iw-iw/zoom)*on/F", "ih/2-(ih/zoom/2)"),                   # push + slide
]


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
                    "hook": sh.get("hook"), "scenes": ids})
    return out


def _scene_at(t: float, scene_times: dict) -> str:
    for sid, (a, b) in scene_times.items():
        if a <= t < b:
            return sid
    return list(scene_times)[-1]


def _shot_list(win: dict, story: dict, scene_times: dict, dur: float) -> list[dict]:
    """Prompt and length for every picture in the Short."""
    scenes = {s["id"]: s for s in story["scenes"]}
    chars = {c["id"]: c for c in story["characters"]}
    n = max(3, math.ceil(dur / SHOT_SEC))
    step = dur / n
    shots = []
    for k in range(n):
        t_long = win["start"] + k * step + step / 2
        s = scenes[_scene_at(t_long, scene_times)]
        present = [chars[c] for c in s.get("characters", []) if c in chars]
        who = present[k % len(present)] if present else None
        who_txt = ("a faceless silhouette" if who and who.get("real") else who["look"]) if who else "a lone figure"
        if k == 0 and win.get("hook"):
            prompt = win["hook"]
        else:
            prompt = TRAILER_SHOTS[k % len(TRAILER_SHOTS)].format(who=who_txt, setting=s["setting"])
        shots.append({"prompt": f"{prompt}, {STYLE_TAIL}", "sec": step, "t_long": t_long})
    return shots


def prepare(story: dict, scene_times: dict, subs: list, work: Path, cfg: dict, style: str) -> int:
    """Plan every Short's pictures and make them (run before the long video is rendered, so the
    images can be built over several mornings). Raises images.QuotaExhausted when the day's
    allowance runs out; finished pictures are kept."""
    made = 0
    for win in windows(story, scene_times, subs):
        d = work / "shorts" / f"s{win['n']:02d}"
        d.mkdir(parents=True, exist_ok=True)
        plan_file = d / "plan.json"
        if plan_file.exists():
            plan = json.loads(plan_file.read_text())
        else:
            plan = {"body": win["end"] - win["start"],
                    "shots": _shot_list(win, story, scene_times, win["end"] - win["start"])}
            plan_file.write_text(json.dumps(plan, indent=1))
        for i, sh in enumerate(plan["shots"]):
            p = d / f"img_{i:02d}.png"
            if not p.exists():
                log(f"  short {win['n']} image {i + 1}/{len(plan['shots'])}")
                images.render(sh["prompt"], p, cfg, 500 + i, SQ, SQ, style)
            made += 1
    return made


def count(story: dict, scene_times: dict, subs: list) -> int:
    return sum(max(3, math.ceil((w["end"] - w["start"]) / SHOT_SEC)) for w in windows(story, scene_times, subs))


def _picture(shot: dict, i: int, d: Path, cfg: dict, style: str, joined: Path) -> Path:
    p = d / f"img_{i:02d}.png"
    if p.exists():
        return p
    try:
        return images.render(shot["prompt"], p, cfg, 500 + i, SQ, SQ, style)
    except Exception as e:  # noqa: BLE001  (quota out: use the long video's own frame)
        log(f"    short image {i}: {e!s:.80} -> frame from the long video")
        fb = d / f"img_{i:02d}_frame.png"
        run(["ffmpeg", "-y", "-ss", f"{shot['t_long']:.2f}", "-i", str(joined), "-frames:v", "1",
             "-vf", f"crop=ih:ih,scale={SQ}:{SQ}", str(fb)])
        return fb


def _captions(rows: list, d: Path, n: int, title: str = "", body: float = 0.0) -> Path:
    """Three words at a time, each chunk timed by its share of the line."""
    events = []
    for s, e, text in rows:
        words = text.replace("\n", " ").split()
        chunks = [" ".join(words[i:i + 3]) for i in range(0, len(words), 3)] or [""]
        span = (e - s) / len(chunks)
        for j, c in enumerate(chunks):
            events.append((s + j * span, s + (j + 1) * span, c))
    top = SQ_Y + SQ + 70
    ass = d / f"short_{n:02d}.ass"
    ass.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n"
        f"Style: S,DejaVu Sans,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,8,50,50,{top},1\n"
        "Style: T,DejaVu Sans,64,&H006EB9DE,&H006EB9DE,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,"
        f"{H - SQ_Y + 30},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        # each chunk pops: starts at 80% size and snaps to 100% in 0.12 s
        + "".join(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},S,,0,0,0,,"
                  f"{{\\fscx80\\fscy80\\t(0,120,\\fscx100\\fscy100)}}{c.upper()}\n" for a, b, c in events)
        + (f"Dialogue: 1,{_ass_time(0)},{_ass_time(body)},T,,0,0,0,,{title}\n" if title else ""),
        encoding="utf-8")
    return ass


def render(win: dict, story: dict, scene_times: dict, subs: list, work: Path, cfg: dict, style: str,
           grade: str) -> Path:
    d = work / "shorts" / f"s{win['n']:02d}"
    d.mkdir(parents=True, exist_ok=True)
    joined, final = work / "joined.mp4", work / f"{story['id']}.mp4"
    a, b = win["start"], win["end"]
    body = b - a
    dur = body + END_SEC
    out = work / "shorts" / f"short_{win['n']:02d}.mp4"

    plan_file = d / "plan.json"
    if plan_file.exists():                       # pictures were planned and made in advance
        plan = json.loads(plan_file.read_text())
        scale = body / plan["body"] if plan["body"] else 1.0
        shots = [{**sh, "sec": sh["sec"] * scale} for sh in plan["shots"]]
    else:
        shots = _shot_list(win, story, scene_times, body)
    pics = [_picture(sh, i, d, cfg, style, joined) for i, sh in enumerate(shots)]
    rows = [(max(0.0, s - a), min(body, e - a), t) for (s, e, t) in subs if e > a and s < b]
    ass = _captions(rows, d, win["n"], win["title"].split("|")[0].strip(), body)
    endtxt = d / "end.txt"
    endtxt.write_text("Watch the full story\non Tall-Tale", encoding="utf-8")

    inputs, fc = [], []
    frames = [max(2, round(sh["sec"] * FPS)) for sh in shots]
    frames[-1] += round(END_SEC * FPS)                       # last picture stays under the end card
    for i, (p, fr) in enumerate(zip(pics, frames)):
        z, x, y = (e.replace("F", str(fr)) for e in MOVES[i % len(MOVES)])
        inputs += ["-i", str(p)]
        fc.append(f"[{i}:v]scale={SQ * 2}:{SQ * 2},zoompan=z='{z}':x='{x}':y='{y}':d={fr}:s={SQ}x{SQ}:fps={FPS},"
                  f"setsar=1[p{i}]")
    k = len(pics)
    cuts = [sum(frames[:i]) / FPS for i in range(1, k)]
    flashes = "+".join(f"between(t,{c:.2f},{c + 0.07:.2f})" for j, c in enumerate(cuts) if j % 3 == 1) or "0"
    fc.append("".join(f"[p{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0,{grade},"
              f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='{flashes}',"
              f"vignette=PI/4,noise=alls=4:allf=t[sq]")
    fc.append("[sq]split=2[s1][s2]")
    fc.append(f"[s1]scale={H}:{H},crop={W}:{H},boxblur=30:2,eq=brightness=-0.18:saturation=0.7[bg]")
    fc.append(f"[bg][s2]overlay=0:{SQ_Y}[v1]")
    li = k + 1  # input index of the logo (k is the audio)
    fc.append(f"[{li}:v]scale=120:120[lg];[v1][lg]overlay={(W - 120) // 2}:36[v3]")
    fc.append(f"[v3]ass='{ass.as_posix()}'[v4]")
    fc.append(f"[v4]drawbox=x=0:y=0:w=iw:h=ih:color=black@0.65:t=fill:enable='gte(t,{body:.2f})',"
              f"drawtext=fontfile={FONT}:textfile='{endtxt.as_posix()}':fontcolor=0xDEB96E:fontsize=76:"
              f"line_spacing=20:x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{body:.2f})',format=yuv420p[v]")
    run(["ffmpeg", "-y", *inputs,
         "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(final),
         "-loop", "1", "-i", str(ROOT / "assets" / "logo.png"),
         "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{k}:a",
         "-af", f"afade=t=out:st={dur - 1.2:.2f}:d=1.2",
         "-t", f"{dur:.2f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "8M",
         "-bufsize", "16M",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)])
    log(f"  short {win['n']}: {dur:.0f}s, {k} pictures -> {out.name}")
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


def make_all(story: dict, scene_times: dict, subs: list, work: Path, cfg: dict, genre: dict) -> list[dict]:
    wins = windows(story, scene_times, subs)
    for w in wins:
        w["file"] = render(w, story, scene_times, subs, work, cfg, genre["style"], genre["grade"])
    return wins
