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

from .common import ROOT, log, retry

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
# Draws a picture FROM up to 4 reference pictures (cast portraits, scene master), so faces, clothes
# and props stay the same from shot to shot. ~125 neurons per 1 MP picture (about Rs 0.12).
CF_REF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
CAST = ROOT / "cast"


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


class Flagged(RuntimeError):
    """The image engine's safety filter rejected this prompt/picture combination (Cloudflare code 3030)."""
    no_retry = True      # asking again with the same input only wastes time


class QuotaExhausted(RuntimeError):
    """The image engine's free daily allowance is used up; carry on tomorrow."""


class ImagesPending(RuntimeError):
    def __init__(self, done: int, total: int, reason: str = ""):
        super().__init__(f"{done}/{total} images ready; {reason}")
        self.done, self.total = done, total


def _cloudflare(prompt: str, out: Path, w: int, h: int, seed: int) -> None:
    """Cloudflare Workers AI, FLUX.1 schnell. Free plan: 10,000 neurons/day (~150 images)."""
    acct, token = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (acct and token):
        raise RuntimeError("CF_ACCOUNT_ID / CF_API_TOKEN not set")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{CF_MODEL}"

    def fetch():
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"},
                          json={"prompt": prompt[:2000], "steps": 6},  # this model rejects "seed"
                          timeout=180)
        if r.status_code == 429 or "4006" in r.text[:300]:
            raise QuotaExhausted(f"Cloudflare {r.status_code}: {r.text[:300]}")
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

    try:
        retry(fetch, attempts=3, base_wait=10.0)
    except QuotaExhausted:
        raise
    except RuntimeError as e:
        if "429" in str(e):
            raise QuotaExhausted(str(e)) from e
        raise


def _ref_png(path: Path) -> bytes:
    im = Image.open(path).convert("RGB")
    im.thumbnail((504, 504))                    # the model wants every input below 512x512
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def _cloudflare_ref(prompt: str, out: Path, w: int, h: int, refs: list[Path]) -> None:
    """FLUX.2 klein: text plus up to 4 reference pictures (input_image_0..3), multipart form."""
    acct, token = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (acct and token):
        raise RuntimeError("CF_ACCOUNT_ID / CF_API_TOKEN not set")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{CF_REF_MODEL}"
    ow, oh = (1344, 768) if w > h * 1.2 else (768, 1344) if h > w * 1.2 else (1024, 1024)

    def fetch():
        files = {"prompt": (None, prompt[:2000]), "width": (None, str(ow)), "height": (None, str(oh))}
        for i, r in enumerate(refs[:4]):
            files[f"input_image_{i}"] = (f"ref{i}.png", _ref_png(r), "image/png")
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, timeout=240)
        if r.status_code == 429 or "4006" in r.text[:300]:
            raise QuotaExhausted(f"Cloudflare {r.status_code}: {r.text[:300]}")
        if r.status_code == 400 and ("3030" in r.text[:400] or "flagged" in r.text[:400].lower()):
            raise Flagged(f"Cloudflare flagged the output: {r.text[:200]}")
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

    retry(fetch, attempts=3, base_wait=10.0)


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


def render(prompt: str, out: Path, cfg: dict, seed: int, w: int, h: int, style: str = "",
           refs: list[Path] | None = None) -> Path:
    """refs: reference pictures the new picture must match (only the cloudflare engine uses them)."""
    if out.exists():
        return out  # resume support: don't regenerate finished images
    icfg = cfg["images"]
    full = f"{prompt}, {style or icfg.get('style_suffix', '')}"
    engine = icfg["engine"]
    refs = [r for r in (refs or []) if r and Path(r).exists()][:4]
    if engine == "cloudflare" and (refs or icfg.get("consistent", True)):
        try:
            try:
                _cloudflare_ref(full, out, w, h, refs)
            except Flagged as fl:
                # the safety filter is touchy about some combinations; never let one shot stop a whole video
                log(f"    shot flagged by the filter ({fl!s:.90}); trying a softer version")
                soft = ("gentle family-friendly storybook illustration, calm and tasteful, no violence, "
                        "no blood, no injury, " + full)
                try:
                    _cloudflare_ref(soft, out, w, h, refs)
                except Flagged:
                    try:
                        _cloudflare_ref(soft, out, w, h, refs[:1])
                    except Flagged:
                        if refs:
                            log("    still flagged; reusing the scene's reference picture for this shot")
                            import shutil
                            shutil.copy(refs[0], out)
                        else:
                            _cloudflare(soft, out, w, h, seed)
        except QuotaExhausted:
            raise
        except RuntimeError as e:
            if refs:
                raise
            log(f"    FLUX.2 klein failed ({e!s:.120}); drawing with schnell instead")
            _cloudflare(full, out, w, h, seed)
    elif engine == "cloudflare":
        _cloudflare(full, out, w, h, seed)
    elif engine == "pollinations":
        _pollinations(full, out, w, h, seed, icfg.get("model", "flux"), icfg.get("negative", ""))
    else:
        _placeholder(full, out, w, h, seed)
    return out


CF_VISION = "@cf/llava-hf/llava-1.5-7b-hf"
_WORDS = {"zero": 0, "no": 0, "none": 0, "one": 1, "a": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def count_people(path: Path) -> int | None:
    """How many people does a vision model see in this picture? None if it cannot tell (never blocks a render)."""
    acct, token = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (acct and token):
        return None
    try:
        im = Image.open(path).convert("RGB")
        im.thumbnail((640, 640))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=85)
        r = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{CF_VISION}",
            headers={"Authorization": f"Bearer {token}"},
            json={"image": list(b.getvalue()),
                  "prompt": "Count the people (humans, including figures, reflections and silhouettes) in this "
                            "picture. Answer with a single number only.",
                  "max_tokens": 8}, timeout=90)
        if r.status_code >= 400:
            return None
        txt = str((r.json().get("result") or {}).get("description", "")).lower()
        for tok in txt.replace(".", " ").replace(",", " ").split():
            if tok.isdigit():
                return int(tok)
            if tok in _WORDS:
                return _WORDS[tok]
    except Exception as e:  # noqa: BLE001  - a failed check must never stop a video
        log(f"    people check unavailable ({e!s:.80})")
    return None


def checked_render(prompt: str, out: Path, cfg: dict, seed: int, w: int, h: int, style: str,
                   refs: list[Path], expect: int | None, fallback: Path | None = None) -> Path:
    """Draw a picture, count the people in it, and redraw (twice at most) if there are more than there
    should be: two drivers, a ghost twice, a twin. After that, fall back to the scene master."""
    for attempt in range(3):
        render(prompt, out, cfg, seed, w, h, style, refs=refs)
        if expect is None or not cfg["images"].get("people_check", True):
            return out
        n = count_people(out)
        try:
            with open(out.parent.parent / "qa.log", "a") as f:
                f.write(f"{out.name} expect={expect} seen={n} attempt={attempt + 1}\n")
        except OSError:
            pass
        if n is None or n <= max(expect, 1) + (0 if expect >= 2 else 0):
            return out
        log(f"    people check: {n} people seen, {expect} expected; redrawing ({attempt + 1}/3)")
        out.unlink(missing_ok=True)
    if fallback and Path(fallback).exists():
        import shutil
        shutil.copy(fallback, out)
        log("    people check failed 3 times; using the scene master for this shot")
        return out
    render(prompt, out, cfg, seed, w, h, style, refs=refs)
    return out


class CastPending(RuntimeError):
    """Cast pictures are drawn and wait for approval before anything else is spent."""


def cast_dir(story: dict) -> Path:
    return CAST / story["id"]


def _cast_items(story: dict) -> list[dict]:
    items = [dict(c, kind="character") for c in story["characters"] if not c.get("real")]
    return items + [dict(p, kind="prop") for p in story.get("props", [])]


def lock_cast(story: dict, cfg: dict, style: str = "") -> dict[str, Path]:
    """Step 0 of every video: one reference picture per character and key prop, kept in cast/<story>/.
    Until cast/<story>/APPROVED exists, stop after drawing them (voices and shots cost nothing yet).
    A picture can be replaced by hand (same file name) before approving; delete one to redraw it."""
    d = cast_dir(story)
    d.mkdir(parents=True, exist_ok=True)
    out = {}
    for it in _cast_items(story):
        p = d / f"{it['id']}.png"
        if not p.exists():
            log(f"  cast: {it['id']}")
            if it["kind"] == "character" and it.get("role") == "ghost" and "no body" in it["look"]:
                prompt = f"reference picture of {it['look']}, centred, plain dark grey background, no text, no letters"
            elif it["kind"] == "character":
                prompt = (f"character reference sheet of {it['look']}: on the left the full body seen from the front, "
                          f"on the right a close-up of the same face; plain neutral grey background, even soft light, no text, no letters, no labels")
            else:
                prompt = f"object reference picture of {it['look']}, centred, plain neutral grey background, even light, no text, no letters"
            base = it.get("derive_from")
            refs0 = [d / f"{base}.png"] if base and (d / f"{base}.png").exists() else []
            if refs0:
                prompt = ("image 1 shows the same man: draw him again, with exactly the same face, hair and "
                          "clothes, in this different state: " + prompt)
            render(prompt, p, cfg, 1000, 1024, 1024, style, refs=refs0)
        out[it["id"]] = p
    if cfg["images"].get("cast_approval", True) and not (d / "APPROVED").exists():
        _cast_sheet(story, out, d / "cast_sheet.jpg")
        raise CastPending(f"cast for '{story['title']}' is ready for approval: cast/{story['id']}/cast_sheet.jpg")
    return out


def _cast_sheet(story: dict, pics: dict[str, Path], out: Path) -> None:
    cell, lab = 360, 40
    cols = 4
    rows = (len(pics) + cols - 1) // cols
    im = Image.new("RGB", (cols * cell, rows * (cell + lab)), (20, 20, 24))
    dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    names = {c["id"]: c.get("name", c["id"]) for c in _cast_items(story)}
    for i, (cid, p) in enumerate(pics.items()):
        x, y = (i % cols) * cell, (i // cols) * (cell + lab)
        t = Image.open(p).convert("RGB")
        t.thumbnail((cell - 8, cell - 8))
        im.paste(t, (x + 4, y + 4))
        dr.text((x + 8, y + cell + 6), f"{names[cid]}  ({cid})", fill=(235, 205, 120), font=font)
    im.save(out, quality=88)


def _formless(story: dict, cid: str) -> bool:
    """A ghost with no body (a light, a mist) is described in words only; a reference picture makes the
    model paste the same object everywhere, even indoors."""
    c = next((x for x in story["characters"] if x["id"] == cid), None)
    return bool(c and c.get("role") == "ghost" and "no body" in c.get("look", ""))


def cast_refs(story: dict, ids: list[str]) -> list[Path]:
    d = cast_dir(story)
    return [d / f"{i}.png" for i in ids if (d / f"{i}.png").exists() and not _formless(story, i)]


def ref_prompt(story: dict, ids: list[str], master: bool, prompt: str, expect: int | None = None,
               props: list[str] | None = None) -> str:
    """Tell the model which reference picture is who."""
    names = {c["id"]: c.get("name", c["id"]) for c in _cast_items(story)}
    parts, k = [], 1
    if master:
        parts.append(f"image {k} shows the place: keep the same location, light, weather and objects, but use a NEW "
                     f"camera angle and framing as described, do not copy its composition")
        k += 1
    for i in ids:
        if (cast_dir(story) / f"{i}.png").exists() and not _formless(story, i):
            parts.append(f"image {k} is a reference sheet of {names.get(i, i)}: draw this person once, with the same "
                         f"face, hair, age and exactly these clothes; never mix their clothes with anyone else's")
            k += 1
    for pid in props or []:
        if (cast_dir(story) / f"{pid}.png").exists():
            parts.append(f"image {k} is the {pid.replace('_', ' ')}: draw this exact object, same shape, colour and "
                         f"condition, undamaged unless the shot says otherwise")
            k += 1
    rules = " Every person and animal appears only once. No text, letters or captions in the picture."
    if expect is not None:
        rules += (f" Exactly {expect} {'person' if expect == 1 else 'people'} in the picture, no twins, no extra "
                  "figures, no reflections of people unless the shot asks for a mirror." if expect
                  else " No people visible in this picture.")
    return (("; ".join(parts) + "." + rules + " ") if parts else "") + prompt


# Camera vocabulary used to vary consecutive shots (never two identical framings in a row).
SHOT_TYPES = [
    "wide establishing shot of {setting}",
    "medium shot inside {setting}",
    "detail close-up of an object in {setting}",
    "low angle shot looking up, {setting}",
    "over-the-shoulder shot, {setting}",
    "high angle shot looking down, {setting}",
]


def plan_shots(bible: dict, line_durs: dict, cfg: dict) -> dict[str, list[dict]]:
    """Split every scene into shots of at most `max_shot_sec`, one camera framing each.

    Returns {scene_id: [{"prompt", "line", "part", "parts"}...]} in order.
    A line may carry its own "shot" (string or list) to override the generated framing.
    """
    import math
    v = cfg["video"]
    max_shot = float(v.get("max_shot_sec", 3.5))
    budget = int(cfg["images"].get("max_images", 110))
    chars = {c["id"]: c for c in bible["characters"]}

    def count(ms):
        return sum(max(1, math.ceil(d / ms)) for sid in line_durs for d in line_durs[sid])

    while count(max_shot) > budget:          # stay inside the free daily image allowance
        max_shot += 0.5
    plan = {}
    for s in bible["scenes"]:
        unseen = set(s.get("unseen", []))               # a voice only: never drawn in this scene
        present = [chars[c] for c in s.get("characters", []) if c not in unseen]
        tag = lambda c: c.get("tag") or c["look"]       # noqa: E731  - short description, long look stays in the cast sheet
        who = "; ".join("a faceless silhouette of a person, seen from behind" if c.get("real") else tag(c)
                        for c in present)
        base = s.get("image_prompt") or s["setting"]
        shots, cycle = [], 0
        for k, (ln, dur) in enumerate(zip(s["lines"], line_durs[s["id"]])):
            parts = max(1, math.ceil(dur / max_shot))
            custom = ln.get("shot")
            custom = [custom] if isinstance(custom, str) else (custom or [])
            spk = chars.get(ln["speaker"])
            for j in range(parts):
                ids = []
                extra = 0
                if j < len(custom):
                    cs = custom[j]
                    if isinstance(cs, dict):      # {"text", "chars": [ids], "base": false} = exact control
                        prompt = cs["text"] + (f", {base}" if cs.get("base", True) else "")
                        ids = list(cs.get("chars", []))
                    else:
                        prompt = f"{cs}, {base}"
                        # a custom shot may show anyone in the scene: give it everyone's reference sheet
                        ids = [c["id"] for c in present]
                elif spk and j == 0 and spk["id"] not in unseen:
                    # the speaker first, then whoever else may share the frame
                    ids = [spk["id"]] + [c["id"] for c in present if c["id"] != spk["id"]]
                    face = "a faceless silhouette of a person" if spk.get("real") else tag(spk)
                    prompt = f"cinematic close-up of {face}, speaking, in {base}"
                elif not shots:
                    prompt = SHOT_TYPES[0].format(setting=base) + (f", featuring {who}" if who else "")
                    ids = [c["id"] for c in present]
                else:
                    cycle = cycle % (len(SHOT_TYPES) - 1) + 1
                    prompt = SHOT_TYPES[cycle].format(setting=base)
                    if who and cycle in (1, 4):
                        prompt += f", featuring {who}"
                        ids = [c["id"] for c in present]
                ids = [i for i in ids if not chars.get(i, {}).get("real") and i not in unseen][:3]
                low = prompt.lower()
                extra = 1 if ("mirror" in low or "reflect" in low or "behind" in low or "window" in low) else 0
                shots.append({"prompt": prompt, "line": k, "part": j, "parts": parts, "chars": ids, "extra": extra})
        plan[s["id"]] = shots
    total = sum(len(v) for v in plan.values())
    log(f"  shot plan: {total} shots, max {max_shot:.1f}s each")
    return plan


def scene_master(story: dict, sid: str, work: Path, cfg: dict, style: str = "") -> Path:
    """One wide picture per scene with its people and props; every shot of the scene is drawn from it,
    so the room, the light and objects (a padlock on a latch...) stay put."""
    s = next(x for x in story["scenes"] if x["id"] == sid)
    chars = {c["id"]: c for c in story["characters"]}
    unseen = set(s.get("unseen", []))
    present = [chars[c] for c in s.get("characters", []) if c in chars and not chars[c].get("real")
               and c not in unseen][:3]
    props = [p for p in s.get("props", [])][: 4 - len(present)]
    d = work / "masters"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{sid}.png"
    if not p.exists():
        log(f"  scene master: {sid}")
        ids = [c["id"] for c in present]
        props = props[:max(0, 4 - len(ids))]
        base = s.get("image_prompt") or s["setting"]
        people = "; ".join(f"{c.get('name', c['id'])}: {c.get('tag') or c['look']}" for c in present)
        prompt = ref_prompt(story, ids, False, f"wide establishing shot of {base}"
                            + (f", with {people}" if people else "")
                            + (f", {s['continuity']}" if s.get("continuity") else ""), expect=len(present), props=props)
        w, h = cfg["video"]["width"], cfg["video"]["height"]
        checked_render(prompt, p, cfg, 7000, int(w * 1.25), int(h * 1.25), style,
                       cast_refs(story, ids) + [cast_dir(story) / f"{x}.png" for x in props
                                                if (cast_dir(story) / f"{x}.png").exists()][:max(0, 4 - len(ids))],
                       len(present))
    return p


def shot_images(plan: dict, work: Path, cfg: dict, style: str = "", story: dict | None = None) -> dict[str, list[Path]]:
    d = work / "shots"
    d.mkdir(parents=True, exist_ok=True)
    w, h = cfg["video"]["width"], cfg["video"]["height"]
    out = {}
    total = sum(len(v) for v in plan.values())
    done = sum(1 for sid, shots in plan.items() for i in range(len(shots)) if (d / f"{sid}_{i:02d}.png").exists())
    if done < total:
        log(f"  shot images: {done}/{total} already made, making the rest")
    scenes = {x["id"]: x for x in (story or {}).get("scenes", [])}
    try:
        for sid, shots in plan.items():
            out[sid] = []
            master = scene_master(story, sid, work, cfg, style) if story else None
            cont = scenes.get(sid, {}).get("continuity")
            for i, sh in enumerate(shots):
                p = d / f"{sid}_{i:02d}.png"
                prompt, refs = sh["prompt"], []
                if story and master and sh["prompt"].startswith("wide establishing shot") and not p.exists():
                    import shutil
                    shutil.copy(master, p)          # the master already is this scene's establishing shot
                if story:
                    ids = sh.get("chars", [])
                    close = any(w in sh["prompt"].lower() for w in ("close-up", "close up", "detail"))
                    use_master = master is not None and not close
                    sprops = [x for x in scenes.get(sid, {}).get("props", [])
                              if (cast_dir(story) / f"{x}.png").exists()] if not close else []
                    sprops = sprops[:max(0, 4 - (1 if use_master else 0) - len(cast_refs(story, ids)))]
                    prompt = ref_prompt(story, ids, use_master, prompt + (f", {cont}" if cont and not close else ""),
                                        expect=len(ids), props=sprops)
                    refs = ([master] if use_master else []) + cast_refs(story, ids) + [
                        cast_dir(story) / f"{x}.png" for x in sprops]
                if not p.exists():
                    log(f"  shot image: {sid} #{i + 1}/{len(shots)}")
                out[sid].append(checked_render(prompt, p, cfg, (i * 7919 + len(sid) * 104729) % 100000,
                                               int(w * 1.25), int(h * 1.25), style, refs,
                                               (len(sh.get("chars", [])) + sh.get("extra", 0)) if story else None,
                                               fallback=master))
    except QuotaExhausted as qe:
        made = sum(1 for s2, sh2 in plan.items() for k in range(len(sh2)) if (d / f"{s2}_{k:02d}.png").exists())
        raise ImagesPending(made, total, str(qe)[:300])
    return out
