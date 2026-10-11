"""Cast + a few real shots for one story, to check consistency before a full render.
python scripts/cast_preview.py drafts/003-jatinga.json s05 s20 s23
Writes cast/<id>/ and cast/<id>/preview/ (scene masters + shots) and a contact sheet."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio import bible as bib, genres, images  # noqa: E402
from studio.common import load_config  # noqa: E402

story = bib.load(Path(sys.argv[1]))
want = sys.argv[2:]
cfg = load_config()
cfg["images"]["cast_approval"] = False
style = genres.get(story)["style"]
images.lock_cast(story, cfg, style)
images._cast_sheet(story, {i["id"]: images.cast_dir(story) / f"{i['id']}.png" for i in images._cast_items(story)},
                   images.cast_dir(story) / "cast_sheet.jpg")
work = images.cast_dir(story) / "preview"
sub = {**story, "scenes": [s for s in story["scenes"] if s["id"] in want]}
plan = images.plan_shots(sub, {s["id"]: [3.0] * len(s["lines"]) for s in sub["scenes"]}, cfg)
plan = {sid: shots[:4] for sid, shots in plan.items()}
images.shot_images(plan, work, cfg, style, sub)
pics = [work / "masters" / f"{sid}.png" for sid in plan] + sorted((work / "shots").glob("*.png"))
cell = 400
im = Image.new("RGB", (cell * 4, (len(pics) + 3) // 4 * (cell * 9 // 16 + 30)), (20, 20, 24))
d = ImageDraw.Draw(im)
for k, p in enumerate(pics):
    t = Image.open(p).convert("RGB")
    t.thumbnail((cell - 6, cell))
    x, y = (k % 4) * cell, (k // 4) * (cell * 9 // 16 + 30)
    im.paste(t, (x + 3, y + 3))
    d.text((x + 6, y + cell * 9 // 16 + 6), p.stem, fill=(235, 205, 120))
im.save(work / "preview_sheet.jpg", quality=86)
print("done")
