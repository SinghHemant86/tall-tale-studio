"""Tall-Tale Studio: render the next locked story in queue/ into a finished, branded video.

  python run.py                      # next story in queue (priority ones first)
  python run.py queue/001-x.json     # a specific story
  python run.py --offline            # placeholder images/voices: tests the pipeline with no internet
  python run.py --no-upload          # render only
"""
import argparse
import json
import os
import sys
from pathlib import Path

from studio import assemble, bible as bib, branding, genres, images, llm, upload, voice
from studio.common import ROOT, load_config, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("story", nargs="?")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--keep-in-queue", action="store_true", help="don't move the story to done/")
    args = ap.parse_args()

    cfg = load_config()
    if os.environ.get("IMAGE_ENGINE"):
        cfg["images"]["engine"] = os.environ["IMAGE_ENGINE"]
    if args.offline:
        cfg["images"]["engine"] = "placeholder"
        cfg["voice"]["engine"] = "placeholder"
        cfg["youtube"]["upload"] = False
    if args.no_upload:
        cfg["youtube"]["upload"] = False

    path = Path(args.story) if args.story else bib.next_in_queue()
    if not path:
        log("Queue is empty — nothing to render. Lock a story in chat and add it to queue/.")
        return 0
    story = bib.load(path)
    genre = genres.get(story)
    brand = cfg.get("branding", {})
    work = ROOT / "output" / story["id"]
    work.mkdir(parents=True, exist_ok=True)
    log(f"Story: {story['title']}  ({genre['name']}, {len(story['scenes'])} scenes)")

    log("1/6 characters")
    portraits = images.character_portraits(story, work, cfg, genre["style"])
    log("2/6 scene images")
    scene_imgs = images.scene_images(story, work, cfg, genre["style"])
    log("3/6 voices")
    lines = voice.speak_all(story, work, cfg, genre)

    log("4/6 clips")
    clips, music_plan, subs, t = [], [], [], 0.0

    def add(clip: Path, mood: str):
        nonlocal t
        d = assemble.duration(clip)
        clips.append(clip)
        music_plan.append((mood, d))
        t += d

    if brand.get("intro", True):
        add(branding.card_clip("intro", brand.get("intro_sec", 4.0), work, cfg), "intro")
    if genre.get("true_story"):
        add(branding.card_clip("disclaimer", 5.0, work, cfg, genres.DISCLAIMER), genre["mood"])
    for s in story["scenes"]:
        clip = assemble.scene_clip(s, scene_imgs[s["id"]], lines[s["id"]], work, cfg, subs, t, genre["grade"])
        add(clip, s.get("mood", genre["mood"]))
    if brand.get("end_card", True):
        note = "Sources are listed in the description" if genre.get("true_story") else ""
        add(branding.card_clip("end", brand.get("end_sec", 7.0), work, cfg, note), "outro")

    log("5/6 music + final mix")
    music = assemble.music_bed(music_plan, work, cfg, genre["name"])
    final = work / f"{story['id']}.mp4"
    assemble.final_video(clips, music, subs, work, cfg, final)
    thumb = branding.thumbnail(story["title"], scene_imgs[story["scenes"][0]["id"]], work / "thumbnail.jpg")
    log(f"   video: {final}  ({t / 60:.1f} min)")

    log("6/6 publish")
    meta = llm.youtube_metadata(story)
    (work / "youtube.json").write_text(json.dumps({"title": story["title"], **meta}, indent=2, ensure_ascii=False))
    vid = upload.upload(final, thumb, story["title"], meta, cfg) if cfg["youtube"]["upload"] else None

    result = {"video": str(final.relative_to(ROOT)), "seconds": round(t, 1), "youtube_id": vid,
              "portraits": [str(p.relative_to(ROOT)) for p in portraits.values()]}
    if not args.keep_in_queue and path.parent.resolve() == bib.QUEUE.resolve():
        bib.mark_done(path, result)
    log("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
