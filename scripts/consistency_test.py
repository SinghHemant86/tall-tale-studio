"""Side-by-side consistency test: today's method (every shot drawn fresh by FLUX.1 schnell) against
reference-image methods (FLUX.2 klein 4B / 9B, each shot drawn FROM a fixed character portrait or
scene master). Writes research/consistency/<engine>/*.png and a labelled contact sheet.

python scripts/consistency_test.py
"""
import base64
import io
import json
import os
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.genres import ART_STYLES  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "research" / "consistency"
STYLE = ART_STYLES["creepy_comic"]
ACCT, TOKEN = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/"

H = "old sandstone haveli with carved arches"
MADHO = "thin Indian man about 60, short white beard, tired kind eyes, faded brown kurta, grey wool shawl"
BOY = "thin 8-year-old Indian village boy, messy hair, torn faded blue half-sleeve shirt, brown shorts, barefoot"
DOOR = f"a heavy carved wooden door in a dark corridor of an {H}, a big rusted iron padlock hanging from the door latch on a chain"

# (name, reference key or None, prompt). Reference keys point at earlier names.
SHOTS = [
    ("madho_ref", None, f"character portrait of {MADHO}, full body, standing, plain dark background"),
    ("madho_bus", "madho_ref", f"{MADHO} stepping down from a battered bus on a dusty road at dusk, rocky hills"),
    ("madho_kitchen", "madho_ref", f"close-up of {MADHO} listening by lantern light in a smoky haveli kitchen"),
    ("madho_corridor", "madho_ref", f"{MADHO} walking with a kerosene lantern down a long dark corridor of an {H}, seen from the side"),
    ("boy_ref", None, f"character portrait of {BOY}, full body, standing, plain dark background"),
    ("boy_play", "boy_ref", f"1986 flashback, warm faded colours: {BOY} laughing, playing hide and seek in a sunlit haveli courtyard"),
    ("boy_mob", "boy_ref", f"1986 flashback, warm faded colours: {BOY} crying as villagers with torches drag his family away at night"),
    ("door_master", None, f"wide shot of {DOOR}, moonlight"),
    ("door_close", "door_master", "extreme close-up of the same rusted padlock hanging from the same door latch, same door, same lighting"),
    ("door_madho", "door_master+madho_ref", f"the same door with the same padlock hanging from its latch, {MADHO} holding up a lantern in front of it"),
]

ENGINES = {
    "A_schnell_today": "@cf/black-forest-labs/flux-1-schnell",
    "B_klein4b_refs": "@cf/black-forest-labs/flux-2-klein-4b",
    "C_klein9b_refs": "@cf/black-forest-labs/flux-2-klein-9b",
}


def _decode(r: requests.Response) -> Image.Image:
    if r.headers.get("content-type", "").startswith("image"):
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    body = r.json()
    res = body.get("result", body)
    img = res.get("image") if isinstance(res, dict) else None
    if not img:
        raise RuntimeError(f"no image in response: {str(body)[:400]}")
    return Image.open(io.BytesIO(base64.b64decode(img))).convert("RGB")


def _png(img: Image.Image, side: int = 504) -> bytes:
    im = img.copy()
    im.thumbnail((side, side))
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def run(model: str, prompt: str, refs: list[Image.Image]) -> tuple[Image.Image, float]:
    head = {"Authorization": f"Bearer {TOKEN}"}
    t = time.time()
    for attempt in range(4):
        if "schnell" in model:
            r = requests.post(URL + model, headers=head, json={"prompt": prompt[:2000], "steps": 6}, timeout=180)
        else:
            files = {"prompt": (None, prompt[:2000]), "width": (None, "1024"), "height": (None, "1024")}
            for i, ref in enumerate(refs[:4]):
                files[f"input_image_{i}"] = (f"ref{i}.png", _png(ref), "image/png")
            r = requests.post(URL + model, headers=head, files=files, timeout=240)
        if r.status_code < 400:
            return _decode(r), time.time() - t
        print(f"::warning title={model}::HTTP {r.status_code} {r.text[:300]}")
        time.sleep(8 * (attempt + 1))
    raise RuntimeError(f"{model} failed: {r.status_code} {r.text[:400]}")


def sheet(results: dict[str, dict[str, Image.Image]]) -> Path:
    cell, pad, lab = 300, 8, 34
    rows, cols = list(results), [s[0] for s in SHOTS]
    W = 190 + len(cols) * (cell + pad)
    Hh = lab + len(rows) * (cell + pad)
    im = Image.new("RGB", (W, Hh), (18, 18, 22))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 17)
    except OSError:
        f = ImageFont.load_default()
    for j, c in enumerate(cols):
        d.text((190 + j * (cell + pad), 8), c, fill=(230, 200, 120), font=f)
    for i, r in enumerate(rows):
        y = lab + i * (cell + pad)
        d.text((8, y + cell // 2), r.replace("_", "\n", 1), fill=(240, 240, 240), font=f)
        for j, c in enumerate(cols):
            if c in results[r]:
                t = results[r][c].copy()
                t.thumbnail((cell, cell))
                im.paste(t, (190 + j * (cell + pad), y))
    p = OUT / "contact_sheet.jpg"
    im.save(p, quality=88)
    return p


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results, timing = {}, {}
    for label, model in ENGINES.items():
        d = OUT / label
        d.mkdir(exist_ok=True)
        made: dict[str, Image.Image] = {}
        for name, ref, prompt in SHOTS:
            refs = [made[k] for k in (ref.split("+") if ref else []) if k in made]
            use_refs = "schnell" not in model and refs
            full = prompt
            if use_refs:
                names = " and ".join(f"image {i + 1}" for i in range(len(refs)))
                full = (f"Keep the exact same person, face, hair, beard, clothes, objects and their positions as in "
                        f"{names}. {prompt}")
            try:
                img, secs = run(model, f"{full}, {STYLE}", refs if use_refs else [])
            except Exception as e:  # noqa: BLE001
                print(f"::error title={label} {name}::{str(e)[:400]}")
                continue
            img.save(d / f"{name}.png")
            made[name] = img
            timing.setdefault(label, []).append(round(secs, 1))
            print(label, name, f"{secs:.1f}s")
        results[label] = made
    print("sheet:", sheet(results))
    (OUT / "timing.json").write_text(json.dumps(timing, indent=1))


if __name__ == "__main__":
    main()
