"""Free-tier LLM with fallback across OpenRouter / Gemini / Groq (all OpenAI-compatible)."""
import os
import re

import requests

from .common import load_config, log


def chat(prompt: str, system: str = "You are a concise assistant.", max_tokens: int = 800) -> str | None:
    cfg = load_config()["llm"]
    for prov in cfg["providers"]:
        key = os.environ.get(prov["key_env"])
        if not key:
            continue
        for model in prov["models"]:
            try:
                r = requests.post(
                    f"{prov['base_url']}/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": model,
                        "max_tokens": max_tokens,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                    },
                    timeout=90,
                )
                if r.status_code == 200:
                    text = r.json()["choices"][0]["message"]["content"]
                    if text and text.strip():
                        log(f"  llm: {prov['name']}/{model}")
                        return text.strip()
                log(f"  llm {prov['name']}/{model} -> HTTP {r.status_code}, trying next")
            except Exception as e:  # noqa: BLE001
                log(f"  llm {prov['name']}/{model} error: {e!s:.120}")
    return None


DEVA = re.compile(r"[\u0900-\u097F]")


def _english(text: str | None) -> bool:
    return bool(text) and not DEVA.search(text)


def youtube_metadata(bible: dict) -> dict:
    """English description, hashtags and tags.

    The description, tags and hashtags are written per story when it is locked (Claude, with the
    yt-seo rules). This only fills gaps: the free LLM writes a description from the English
    subtitles if none was given, else the English logline is used. Genre and channel terms are added.
    """
    from .genres import CHANNEL_TAGS, SEO, get as genre_of, text
    yt = dict(bible.get("youtube") or {})
    genre = bible.get("genre", "horror")
    if not _english(yt.get("description")):
        story = " ".join(ln.get("en") or ln["text"] for s in bible["scenes"] for ln in s["lines"])
        desc = chat(
            "Write a gripping 2-3 sentence YouTube description in English for this Hindi-narrated story. "
            "Put the most searchable phrase in the first sentence. No spoilers, no hashtags, no emojis.\n\n"
            f"Title: {bible['title']}\nStory: {story[:3000]}",
            max_tokens=300,
        )
        yt["description"] = desc if _english(desc) else bible.get("logline", bible["title"])

    # hashtags: the story's own first (place, theme), then genre, then the channel. YouTube shows
    # the first three above the title; more than 15 makes it ignore them all, so keep it short.
    tags_h = list(yt.get("hashtags") or []) + SEO.get(genre, {}).get("hashtags", []) + ["#TallTale"]
    hashtags, seen = [], set()
    for h in tags_h:
        h = "#" + re.sub(r"[^A-Za-z0-9]", "", h.lstrip("#"))
        if len(h) > 2 and h.lower() not in seen:
            seen.add(h.lower())
            hashtags.append(h)
    hashtags = hashtags[:6]

    parts = [yt["description"].strip()]
    if genre_of(bible).get("true_story"):
        parts.append(text(bible, "disclaimer").replace("\n", " "))
        parts.append(text(bible, "sources_head") + "\n" + "\n".join(f"- {s}" for s in bible.get("sources", [])))
    parts.append(text(bible, "footer"))
    parts.append(" ".join(hashtags))
    yt["description"] = "\n\n".join(parts)

    # tags: story-specific first, then genre, then channel; English only, YouTube's 500-char limit
    tags, total, seen = [], 0, set()
    for t in list(yt.get("tags") or []) + SEO.get(genre, {}).get("tags", []) + CHANNEL_TAGS:
        t = t.strip()
        if not t or DEVA.search(t) or t.lower() in seen:
            continue
        cost = len(t) + (2 if " " in t else 0) + 1
        if total + cost > 480:
            break
        seen.add(t.lower())
        tags.append(t)
        total += cost
    yt["tags"] = tags
    yt["hashtags"] = hashtags
    yt["text_language"], yt["audio_language"] = "en", ("en" if bible.get("language") == "en" else "hi")
    return yt
