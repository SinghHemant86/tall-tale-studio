"""Render the same two scenes in every art style, for choosing a channel look (saved to research/styles/)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio import images  # noqa: E402
from studio.common import ROOT, load_config  # noqa: E402
from studio.genres import ART_STYLES, GENRES  # noqa: E402

SCENES = {
    "door": "an old Indian night watchman in khaki uniform with a brass torch, standing in a dark abandoned "
            "chawl corridor, facing a sealed wooden door marked 4B, monsoon rain outside",
    "ghost": "a pale woman in a white saree behind frosted glass, long wet black hair hiding her face, "
             "long bony twisted fingers pressed on the glass",
}
cfg = load_config()
out = ROOT / "research" / "styles"
out.mkdir(parents=True, exist_ok=True)
for name, style in ART_STYLES.items():
    for sid, prompt in SCENES.items():
        p = out / f"{name}_{sid}.png"
        images.render(prompt, p, cfg, 7, 1024, 576, style or GENRES["horror"]["style"])
        print("rendered", p.name)
