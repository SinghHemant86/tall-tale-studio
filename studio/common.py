"""Shared helpers: config, logging, ffmpeg calls."""
import json
import subprocess
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd: list[str]) -> None:
    """Run ffmpeg/ffprobe quietly; raise with stderr on failure."""
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd[:6])}...\n{res.stderr[-2000:]}")


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def retry(fn, attempts: int = 4, base_wait: float = 4.0):
    """Call fn(); on exception wait and retry with backoff."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            wait = base_wait * (2 ** i)
            log(f"  retry {i + 1}/{attempts} after error: {e!s:.160} (waiting {wait:.0f}s)")
            time.sleep(wait)
    raise last
