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


def youtube_metadata(bible: dict) -> dict:
    """Fill description/tags if the bible left them empty. Falls back to plain text."""
    yt = dict(bible.get("youtube") or {})
    if not yt.get("description"):
        story = " ".join(ln["text"] for s in bible["scenes"] for ln in s["lines"])
        from .genres import language
        lang = ("Write it in Hindi, in Devanagari script only (no English words). "
                if language(bible) == "hi" else "")
        desc = chat(
            "Write a gripping 3-sentence YouTube description for this story. " + lang +
            "No spoilers for the ending, no hashtags, no emojis.\n\n"
            f"Title: {bible['title']}\nStory: {story[:3000]}",
            max_tokens=300,
        )
        if language(bible) == "hi":
            # must really be Hindi; otherwise use the story's own opening lines
            if not desc or len(re.findall(r"[A-Za-z]{2,}", desc)) > 2:
                desc = bible.get("logline_hi") or " ".join(
                    ln["text"] for s in bible["scenes"] for ln in s["lines"] if ln["speaker"] == "narrator")[:280]
        yt["description"] = desc or bible.get("logline", bible["title"])
    from .genres import get as genre_of, text
    parts = [yt["description"].strip()]
    if genre_of(bible).get("true_story"):
        parts.append(text(bible, "disclaimer").replace("\n", " "))
        parts.append(text(bible, "sources_head") + "\n" + "\n".join(f"- {s}" for s in bible.get("sources", [])))
    parts.append(text(bible, "footer"))
    yt["description"] = "\n\n".join(parts)
    yt.setdefault("tags", ["tall tale", "story", bible.get("genre", "horror").replace("_", " ")])
    return yt
