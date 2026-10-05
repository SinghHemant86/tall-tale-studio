"""Character portraits + scene images.

Consistency trick: every prompt that shows a character repeats that character's exact
'look' text and uses the character's fixed seed, so faces/outfits stay close across scenes.
"""
import base64
import io
import os
import urllib.parse
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .common import log, retry

POLLINATIONS = "https://image.pollinations.ai/prompt/"


def _pollinations(prompt: str, out: Path, w: int, h: int, seed: int, model: str, negative: str) -> None:
    params = {"width": w, "height": h, "seed": seed, "model": model,
              "nologo": "true", "enhance": "false", "negative": negative}
    token = os.environ.get("POLLINATIONS_TOKEN")  # optional; raises rate limits if you register
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = POLLINATIONS + urllib.parse.quote(prompt) + "?" + urllib.parse.urlencode(params)

    def fetch():
        r = requests.get(url, headers=headers, timeout=180)
        r.raise_for_status()
        if not r.headers.get("content-type", "").startswith("image"):
            raise RuntimeError(f"not an image: {r.text[:120]}")
        out.write_bytes(r.content)

    retry(fetch)
    Image.open(out).convert("RGB").save(out)  # normalise to PNG/RGB


CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"


def _fit(img: Image.Image, w: int, h: int) -> Image.Image:
    """Centre-crop to the target aspect ratio, then resize (FLUX on Workers AI returns squares)."""
    iw, ih = img.size
    target = w / h
    if iw / ih > target:
        nw = int(ih * target)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / target)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    return img.resize((w, h), Image.LANCZOS)


def _cloudflare(prompt: str, out: Path, w: int, h: int, seed: int) -> None:
    """Cloudflare Workers AI, FLUX.1 schnell. Free plan: 10,000 neurons/day (~150 images)."""
    acct, token = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (acct and token):
        raise RuntimeError("CF_ACCOUNT_ID / CF_API_TOKEN not set")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{CF_MODEL}"

    def fetch():
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"},
                          json={"prompt": prompt[:2000], "steps": 6, "seed": seed % 2_147_483_647},
                          timeout=180)
        if r.status_code == 429:
            raise RuntimeError("Cloudflare rate limit (429)")
        if r.status_code >= 400:
            raise RuntimeError(f"Cloudflare HTTP {r.status_code}: {r.text[:400]}")
        if r.headers.get("content-type", "").startswith("image"):
            data = r.content
        else:
            body = r.json()
            if not body.get("success", True):
                raise RuntimeError(f"Cloudflare error: {body.get('errors')}")
            data = base64.b64decode(body["result"]["image"])
        _fit(Image.open(io.BytesIO(data)).convert("RGB"), w, h).save(out)

    retry(fetch)


def _placeholder(prompt: str, out: Path, w: int, h: int, seed: int) -> None:
    """Offline stand-in: dark gradient with the prompt text, so the pipeline can be tested."""
    import random
    rnd = random.Random(seed)
    base = (rnd.randint(10, 40), rnd.randint(10, 30), rnd.randint(20, 50))
    img = Image.new("RGB", (w, h), base)
    d = ImageDraw.Draw(img)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c * (1.4 - k)) for c in base))
    try:
        font = ImageFont.truetype("DejaVuSerif.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    words, lines, cur = prompt.split(), [], ""
    for wd in words[:60]:
        if len(cur) + len(wd) > 60:
            lines.append(cur)
            cur = ""
        cur += wd + " "
    lines.append(cur)
    d.multiline_text((60, h // 3), "\n".join(lines[:6]), fill=(170, 160, 150), font=font, spacing=8)
    img.filter(ImageFilter.GaussianBlur(0.6)).save(out)


def render(prompt: str, out: Path, cfg: dict, seed: int, w: int, h: int, style: str = "") -> Path:
    if out.exists():
        return out  # resume support: don't regenerate finished images
    icfg = cfg["images"]
    full = f"{prompt}, {style or icfg.get('style_suffix', '')}"
    engine = icfg["engine"]
    if engine == "cloudflare":
        _cloudflare(full, out, w, h, seed)
    elif engine == "pollinations":
        _pollinations(full, out, w, h, seed, icfg.get("model", "flux"), icfg.get("negative", ""))
    else:
        _placeholder(full, out, w, h, seed)
    return out


def character_portraits(bible: dict, work: Path, cfg: dict, style: str = "") -> dict[str, Path]:
    d = work / "characters"
    d.mkdir(parents=True, exist_ok=True)
    out = {}
    for c in bible["characters"]:
        if c.get("real"):
            log(f"  portrait: {c['name']} skipped (real person)")
            continue
        log(f"  portrait: {c['name']}")
        out[c["id"]] = render(f"portrait of {c['look']}, facing camera, dark background",
                              d / f"{c['id']}.png", cfg, c.get("seed", 1000), 768, 1024, style)
    return out


def scene_images(bible: dict, work: Path, cfg: dict, style: str = "") -> dict[str, Path]:
    d = work / "scenes"
    d.mkdir(parents=True, exist_ok=True)
    chars = {c["id"]: c for c in bible["characters"]}
    w, h = cfg["video"]["width"], cfg["video"]["height"]
    out = {}
    for i, s in enumerate(bible["scenes"]):
        present = [chars[cid] for cid in s.get("characters", [])]
        # real people are never drawn recognisably: they appear only as a faceless silhouette
        who = "; ".join("a faceless silhouette of a person, seen from behind" if c.get("real") else c["look"]
                        for c in present)
        prompt = s.get("image_prompt") or (s["setting"] + (f", featuring {who}" if who else ""))
        seed = present[0].get("seed", 1000) + i if present else 7000 + i
        log(f"  scene image: {s['id']}")
        # render a bit larger than the frame so the Ken Burns motion has room to move
        out[s["id"]] = render(prompt, d / f"{s['id']}.png", cfg, seed, int(w * 1.25), int(h * 1.25), style)
    return out
