"""Tall-Tale channel branding: intro card, optional true-events card, end card, thumbnail.

Brand colours come from the logo: deep navy ground, antique gold.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .common import ROOT, run

NAVY = (17, 22, 38)
NAVY_LIGHT = (32, 42, 70)
GOLD = (222, 185, 110)
GOLD_DIM = (160, 130, 80)
ASSETS = ROOT / "assets"


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    # Cinzel (downloaded in the workflow) matches the logo's lettering; fall back to a serif.
    for name in ([str(ASSETS / "fonts" / "Cinzel.ttf")] +
                 (["DejaVuSerif-Bold.ttf", "NotoSerif-Bold.ttf"] if bold else ["DejaVuSerif.ttf", "NotoSerif-Regular.ttf"])):
        try:
            f = ImageFont.truetype(name, size)
            if name.endswith("Cinzel.ttf"):
                try:
                    f.set_variation_by_name("Bold" if bold else "Regular")
                except Exception:  # noqa: BLE001
                    pass
            return f
        except OSError:
            continue
    return ImageFont.load_default()


def _ground(w: int, h: int) -> Image.Image:
    """Navy radial vignette like the banner background."""
    img = Image.new("RGB", (w, h), NAVY)
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((w * 0.15, -h * 0.2, w * 0.85, h * 1.2), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(w // 8))
    return Image.composite(Image.new("RGB", (w, h), NAVY_LIGHT), img, glow)


def _center_text(d: ImageDraw.ImageDraw, w: int, y: int, text: str, font, fill) -> int:
    box = d.multiline_textbbox((0, 0), text, font=font, align="center", spacing=10)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.multiline_text(((w - tw) / 2, y), text, font=font, fill=fill, align="center", spacing=10)
    return y + th


def _card_png(kind: str, w: int, h: int, out: Path, text: str = "") -> Path:
    img = _ground(w, h)
    d = ImageDraw.Draw(img)
    logo = Image.open(ASSETS / "logo.png").convert("RGBA")
    if kind == "intro":
        s = int(h * 0.62)
        img.paste(logo.resize((s, s), Image.LANCZOS), ((w - s) // 2, int(h * 0.12)), logo.resize((s, s)))
        _center_text(d, w, int(h * 0.80), "A TALL-TALE PRESENTATION", _font(int(h * 0.035)), GOLD_DIM)
    elif kind == "disclaimer":
        _center_text(d, w, int(h * 0.38), text, _font(int(h * 0.045), bold=False), GOLD)
    elif kind == "end":
        s = int(h * 0.42)
        img.paste(logo.resize((s, s), Image.LANCZOS), ((w - s) // 2, int(h * 0.08)), logo.resize((s, s)))
        y = _center_text(d, w, int(h * 0.56), "Thank you for listening", _font(int(h * 0.055)), GOLD)
        y = _center_text(d, w, y + int(h * 0.04), "Subscribe to Tall-Tale for the next story",
                         _font(int(h * 0.038), bold=False), GOLD_DIM)
        if text:
            _center_text(d, w, y + int(h * 0.05), text, _font(int(h * 0.028), bold=False), GOLD_DIM)
    img.save(out)
    return out


def card_clip(kind: str, seconds: float, work: Path, cfg: dict, text: str = "") -> Path:
    """Still card with a gentle push-in and fades, plus a silent stereo track (music is added later)."""
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    d = work / "clips"
    d.mkdir(parents=True, exist_ok=True)
    png = _card_png(kind, w * 2, h * 2, work / f"card_{kind}.png", text)
    out = d / f"_{kind}.mp4"
    frames = int(seconds * fps)
    run(["ffmpeg", "-y", "-i", str(png), "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={seconds}",
         "-filter_complex",
         f"[0:v]zoompan=z='1+0.04*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={fps},"
         f"fade=t=in:st=0:d=0.6,fade=t=out:st={seconds - 0.6:.2f}:d=0.6,format=yuv420p[v]",
         "-map", "[v]", "-map", "1:a", "-t", f"{seconds}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", str(out)])
    return out


def thumbnail(title: str, scene_img: Path, out: Path) -> Path:
    W, H = 1280, 720
    img = Image.open(scene_img).convert("RGB").resize((W, H))
    img = ImageEnhance.Brightness(ImageEnhance.Color(img).enhance(0.7)).enhance(0.85)
    # navy gradient from the bottom so the gold title reads
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        sd.line([(0, y), (W, y)], fill=int(235 * max(0, (y - H * 0.35) / (H * 0.65))))
    img = Image.composite(Image.new("RGB", (W, H), NAVY), img, shade)
    d = ImageDraw.Draw(img)
    font = _font(86)
    words, lines, cur = title.upper().split(), [], ""
    for wd in words:
        if len(cur) + len(wd) > 18:
            lines.append(cur.strip())
            cur = ""
        cur += wd + " "
    lines.append(cur.strip())
    lines = lines[:3]
    y = H - 60 - 104 * len(lines)
    for ln in lines:
        d.text((56, y), ln, font=font, fill=GOLD, stroke_width=4, stroke_fill=(8, 10, 18))
        y += 104
    logo = Image.open(ASSETS / "logo.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
    img.paste(logo, (W - 175, 25), logo)
    img.save(out, quality=92)
    return out
