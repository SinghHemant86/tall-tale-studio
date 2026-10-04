"""Scene clips (Ken Burns motion + horror grade), music bed with ducking, subtitles, thumbnail."""
import random
from pathlib import Path

from .common import ROOT, duration, log, run

MOTIONS = {
    # zoom expression, x expression, y expression   (F = total frames, on = current frame)
    "zoom_in":      ("1+0.12*on/F", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "zoom_in_fast": ("1+0.30*on/F", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "zoom_out":     ("1.18-0.18*on/F", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pan_right":    ("1.12", "(iw-iw/zoom)*on/F", "ih/2-(ih/zoom/2)"),
    "pan_left":     ("1.12", "(iw-iw/zoom)*(1-on/F)", "ih/2-(ih/zoom/2)"),
    "drift_up":     ("1.12", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/F)"),
}


def _srt_time(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


def _find_audio(folder: Path, name: str) -> Path | None:
    files = sorted(p for p in folder.glob(f"{name}*") if p.suffix.lower() in (".mp3", ".wav", ".ogg", ".m4a"))
    return files[0] if files else None


def scene_clip(scene: dict, image: Path, lines: list, work: Path, cfg: dict, subs: list, t0: float,
               grade: str = "eq=saturation=0.75:contrast=1.08:brightness=-0.03") -> Path:
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    gap, pad = v["line_gap_sec"], v["scene_padding_sec"]
    sid = scene["id"]
    out = work / "clips" / f"{sid}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1) scene audio: lines separated by gaps, padded at the end; record subtitle timings
    inputs, parts, t = [], [], 0.6  # short breath before the first line
    for k, (path, secs, text) in enumerate(lines):
        inputs += ["-i", str(path)]
        parts.append(f"[{k}:a]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={gap}[l{k}]")
        subs.append((t0 + t, t0 + t + secs, text))
        t += secs + gap
    n = len(lines)
    concat = "".join(f"[l{k}]" for k in range(n))
    total = t + pad
    fc = ";".join(parts) + f";anullsrc=r=44100:cl=mono:d=0.6[pre];[pre]{concat}concat=n={n + 1}:v=0:a=1,apad=whole_dur={total:.2f}[voice]"

    # optional SFX at the start of the scene (sfx/<name>*.mp3)
    sfx_files = [p for p in (_find_audio(ROOT / "sfx", s) for s in scene.get("sfx", [])) if p]
    for j, p in enumerate(sfx_files):
        inputs += ["-i", str(p)]
        fc += f";[{n + j}:a]aresample=44100,aformat=channel_layouts=mono,volume=0.7[x{j}]"
    if sfx_files:
        mix_in = "[voice]" + "".join(f"[x{j}]" for j in range(len(sfx_files)))
        fc += f";{mix_in}amix=inputs={1 + len(sfx_files)}:duration=first:normalize=0[aout]"
    else:
        fc += ";[voice]anull[aout]"

    # 2) video: Ken Burns motion on the still + horror grade (vignette, grain, slight desaturation)
    frames = int(total * fps)
    z, x, y = MOTIONS.get(scene.get("motion", "zoom_in"), MOTIONS["zoom_in"])
    z, x, y = (e.replace("F", str(frames)) for e in (z, x, y))
    img_idx = len(inputs) // 2
    inputs += ["-i", str(image)]
    fc += (
        f";[{img_idx}:v]scale={w * 2}:-2,zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps},"
        f"{grade},vignette=PI/4.5,noise=alls=7:allf=t,"
        f"fade=t=in:st=0:d=0.5,fade=t=out:st={max(0, total - 0.5):.2f}:d=0.5,format=yuv420p[vout]"
    )

    run(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
         "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", str(out)])
    return out


def music_bed(segments: list[tuple[str, float]], work: Path, cfg: dict) -> Path:
    """One music segment per (mood, seconds) pair, each faded in and out, joined end to end."""
    mcfg = cfg["music"]
    folder = ROOT / mcfg["folder"]
    out = work / "music_bed.wav"
    segs = []
    for i, (mood, dur) in enumerate(segments):
        mood = mood or mcfg["default_mood"]
        track = _find_audio(folder, f"{mood}_") or _find_audio(folder, "")
        seg = work / f"music_{i:02d}.wav"
        if track:
            offset = random.Random(i).uniform(0, max(0, duration(track) - dur - 1))
            run(["ffmpeg", "-y", "-stream_loop", "-1", "-ss", f"{offset:.1f}", "-i", str(track),
                 "-t", f"{dur:.2f}", "-af", "afade=t=in:d=1,afade=t=out:st={:.2f}:d=1".format(max(0, dur - 1)),
                 "-ar", "44100", "-ac", "2", str(seg)])
        else:
            # no music downloaded yet: low synthetic drone so the video still has atmosphere
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.25:d={dur:.2f}",
                 "-f", "lavfi", "-i", f"sine=frequency=55:duration={dur:.2f}",
                 "-filter_complex", "[0:a]lowpass=f=180[n];[1:a]volume=0.25[s];[n][s]amix=inputs=2,"
                 f"afade=t=in:d=1,afade=t=out:st={max(0, dur - 1):.2f}:d=1",
                 "-ar", "44100", "-ac", "2", str(seg)])
        segs.append(seg)
    lst = work / "music_list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def final_video(clips: list[Path], music: Path, subs: list, work: Path, cfg: dict, out: Path) -> Path:
    lst = work / "clips.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips))
    joined = work / "joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])

    srt = work / "subs.srt"
    srt.write_text("\n".join(f"{i + 1}\n{_srt_time(a)} --> {_srt_time(b)}\n{txt}\n"
                             for i, (a, b, txt) in enumerate(subs)), encoding="utf-8")

    mcfg = cfg["music"]
    duck = ("[m][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[md]"
            if mcfg.get("duck", True) else "[m]anull[md]")
    vf = "[0:v]null[v]"
    if cfg["video"].get("subtitles", True):
        font = cfg["video"].get("subtitle_font", "Noto Sans")
        style = (f"FontName={font},FontSize=20,PrimaryColour=&H00E6E6E6,OutlineColour=&H00000000,"
                 "BorderStyle=1,Outline=2,Shadow=0,MarginV=40")
        vf = f"[0:v]subtitles='{srt.as_posix()}':force_style='{style}'[v]"
    fc = (f"[1:a]volume={mcfg['volume_db']}dB[m];[0:a]asplit=2[vmix][vsc];{duck};"
          f"[vmix][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[a];{vf}")
    run(["ffmpeg", "-y", "-i", str(joined), "-i", str(music), "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    return out
