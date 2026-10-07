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

from studio import assemble, bible as bib, branding, genres, images, llm, schedule, shorts, upload, voice
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
    cfg["story_language"] = genres.language(story)
    work = ROOT / "output" / story["id"]
    work.mkdir(parents=True, exist_ok=True)
    log(f"Story: {story['title']}  ({genre['name']}, {len(story['scenes'])} scenes)")

    log("1/6 voices")
    lines = voice.speak_all(story, work, cfg, genre)
    log("2/6 shot plan + images")
    plan = images.plan_shots(story, {sid: [c[1] for c in v] for sid, v in lines.items()}, cfg)
    shot_imgs = images.shot_images(plan, work, cfg, genre["style"])
    log("3/6 thumbnail image")
    tcfg = story.get("thumbnail") or {}
    if tcfg.get("prompt"):
        thumb_img = images.render(tcfg["prompt"] + ", dramatic single subject, strong contrast, empty dark space on the left",
                                  work / "thumbnail_base.png", cfg, 4242, 1280, 720, genre["style"])
    else:
        thumb_img = shot_imgs[story["scenes"][0]["id"]][0]
    portraits = {}

    log("4/6 clips")
    clips, music_plan, subs, t = [], [], [], 0.0
    scene_times = {}

    def add(clip: Path, mood: str):
        nonlocal t
        d = assemble.duration(clip)
        clips.append(clip)
        music_plan.append((mood, d))
        t += d

    if brand.get("intro", True):
        add(branding.card_clip("intro", brand.get("intro_sec", 4.0), work, cfg), "intro")
    if genre.get("true_story"):
        add(branding.card_clip("disclaimer", 5.0, work, cfg, genres.text(story, "disclaimer")), genre["mood"])
    for s in story["scenes"]:
        clip = assemble.scene_clip(s, shot_imgs[s["id"]], lines[s["id"]], work, cfg, subs, t, genre["grade"],
                                   shots=plan[s["id"]])
        start = t
        add(clip, s.get("mood", genre["mood"]))
        scene_times[s["id"]] = (start, t)
    if brand.get("end_card", True):
        note = genres.text(story, "sources") if genre.get("true_story") else ""
        add(branding.card_clip("end", brand.get("end_sec", 7.0), work, cfg, note), "outro")

    log("5/6 music + final mix")
    music = assemble.music_bed(music_plan, work, cfg, genre["name"])
    final = work / f"{story['id']}.mp4"
    assemble.final_video(clips, music, subs, work, cfg, final)
    thumb = branding.thumbnail(tcfg.get("text") or story["title"], thumb_img, work / "thumbnail.jpg")
    log(f"   video: {final}  ({t / 60:.1f} min)")
    short_list = []
    if cfg.get("shorts", {}).get("enabled", True) and story.get("shorts"):
        log("   shorts")
        short_list = shorts.make_all(story, scene_times, subs, work, cfg, genre)

    log("6/6 publish")
    meta = llm.youtube_metadata(story)
    (work / "youtube.json").write_text(json.dumps({"title": story["title"], **meta}, indent=2, ensure_ascii=False))
    scfg = cfg["youtube"].get("schedule", {})
    long_slot, short_slots = (schedule.plan(scfg, len(short_list)) if scfg.get("enabled") else (None, []))
    vid = None
    if cfg["youtube"]["upload"]:
        vid = upload.upload(final, thumb, story["title"], meta, cfg,
                            schedule.rfc3339_utc(long_slot) if long_slot else None)
    short_ids = []
    if vid and short_list and cfg.get("shorts", {}).get("upload", True):
        tags_line = " ".join((meta.get("hashtags") or [])[:3])
        for k, sh in enumerate(short_list):
            smeta = {**meta, "description": f"Full story ▶ https://youtu.be/{vid}\n\n{tags_line} #Shorts\n\n"
                                            "Visuals and voices are AI-generated."}
            slot = schedule.rfc3339_utc(short_slots[k]) if short_slots else None
            short_ids.append(upload.upload(sh["file"], None, f"{sh['title'].split('|')[0].strip()[:90]} #Shorts",
                                           smeta, cfg, slot))
    if vid and long_slot:
        schedule.commit(long_slot, short_slots[:len(short_ids)])

    # keep a copy of the thumbnail in the repo, so it can be checked without downloading the video
    import shutil
    (bib.DONE / "thumbs").mkdir(parents=True, exist_ok=True)
    shutil.copy(thumb, bib.DONE / "thumbs" / f"{story['id']}.jpg")
    result = {"video": str(final.relative_to(ROOT)), "seconds": round(t, 1), "youtube_id": vid,
              "publish_at": long_slot.isoformat() if long_slot else None,
              "shorts": [{"file": str(s["file"].relative_to(ROOT)), "youtube_id": short_ids[i] if i < len(short_ids) else None,
                          "publish_at": short_slots[i].isoformat() if i < len(short_slots) else None}
                         for i, s in enumerate(short_list)],
              "portraits": [str(p.relative_to(ROOT)) for p in portraits.values()]}
    if not args.keep_in_queue and path.parent.resolve() == bib.QUEUE.resolve():
        bib.mark_done(path, result)
    log("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
