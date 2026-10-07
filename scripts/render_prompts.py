"""Render a JSON {name: prompt} with the pipeline's image engine: python scripts/render_prompts.py <file.json> [size]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio import images  # noqa: E402
from studio.common import load_config  # noqa: E402

src = Path(sys.argv[1])
size = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
cfg = load_config()
for name, prompt in json.loads(src.read_text()).items():
    for seed in (11, 23):
        p = src.parent / f"{name}_{seed}.png"
        try:
            images.render(prompt, p, cfg, seed, size, size, " ")
        except Exception as e:  # noqa: BLE001
            print(f"::error title=render {name}::{str(e)[:400]}")
            raise
        print("rendered", p.name)
