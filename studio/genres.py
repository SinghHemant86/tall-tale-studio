"""Genre presets: each story's "genre" picks its visual style, colour grade, narrator delivery and music.

Anything set in the story file itself (a scene's mood, a character's rate) still wins.
"""

GENRES = {
    "horror": {
        "style": "cinematic horror film still, low-key lighting, volumetric fog, deep shadows, "
                 "muted desaturated colors, 35mm film grain, highly detailed",
        "grade": "eq=saturation=0.70:contrast=1.10:brightness=-0.04",
        "narrator_rate": "-8%", "narrator_pitch": "-6Hz",
        "mood": "dread",
    },
    "thriller": {
        "style": "tense thriller film still, cold blue-grey color palette, hard contrast, "
                 "neon reflections on wet streets, shallow depth of field, cinematic",
        "grade": "eq=saturation=0.80:contrast=1.15:brightness=-0.02,colorbalance=bs=0.06:ms=0.03",
        "narrator_rate": "-2%", "narrator_pitch": "-3Hz",
        "mood": "pulse",
    },
    "psychological": {
        "style": "psychological thriller film still, unsettling symmetrical framing, extreme close-up, "
                 "sickly green and amber tones, distorted reflections, claustrophobic, cinematic",
        "grade": "eq=saturation=0.75:contrast=1.08:brightness=-0.03,colorbalance=gm=0.05:rh=0.04",
        "narrator_rate": "-10%", "narrator_pitch": "-4Hz",
        "mood": "drone",
    },
    "dark_drama": {
        "style": "dark drama film still, warm but faded colors, window light, melancholic, "
                 "intimate framing, 16mm film grain, cinematic",
        "grade": "eq=saturation=0.85:contrast=1.04:brightness=-0.02,colorbalance=rm=0.04:bh=-0.03",
        "narrator_rate": "-6%", "narrator_pitch": "-2Hz",
        "mood": "piano",
    },
    "true_incident": {
        "style": "documentary reconstruction still, archival photograph look, muted sepia and grey, "
                 "faces obscured or turned away, silhouettes, no identifiable people, newspaper-era grain",
        "grade": "eq=saturation=0.45:contrast=1.06:brightness=-0.02",
        "narrator_rate": "-4%", "narrator_pitch": "-2Hz",
        "mood": "ambient",
        "true_story": True,
    },
}

DEFAULT = "horror"
DISCLAIMER = "Based on true events.\nSome scenes are dramatised and some names have been changed."
# All on-screen and YouTube text is English; only the audio is Hindi.
TEXT = {"disclaimer": DISCLAIMER, "presents": "A TALL-TALE PRESENTATION", "thanks": "Thank you for listening",
        "subscribe": "Subscribe to Tall-Tale for the next story", "sources": "Sources are listed in the description",
        "sources_head": "Sources:",
        "footer": "Tall-Tale: thrillers, dark dramas, horror and true stories, narrated in Hindi.\n"
                  "Visuals and voices are AI-generated."}

# Genre-level search terms, added to each story's own (story-specific ones come first).
SEO = {
    "horror": {"hashtags": ["#HindiHorrorStory", "#HorrorStories"],
               "tags": ["hindi horror story", "horror story in hindi", "bhoot ki kahani", "scary story", "ghost story"]},
    "thriller": {"hashtags": ["#HindiThriller", "#ThrillerStory"],
                 "tags": ["hindi thriller story", "suspense story in hindi", "thriller story", "mystery story"]},
    "psychological": {"hashtags": ["#PsychologicalThriller", "#HindiStory"],
                      "tags": ["psychological thriller hindi", "dark psychological story", "mind bending story"]},
    "dark_drama": {"hashtags": ["#DarkDrama", "#HindiStory"],
                   "tags": ["dark drama hindi", "emotional dark story", "hindi kahani"]},
    "true_incident": {"hashtags": ["#TrueStory", "#TrueCrimeHindi"],
                      "tags": ["true story hindi", "real incident", "true crime hindi", "sacchi ghatna"]},
}
CHANNEL_TAGS = ["tall tale", "tall-tale stories", "hindi story"]


def language(bible: dict) -> str:
    """'hi' (channel default) or 'en'. 'hinglish' is no longer used: a story is all Hindi or all English."""
    from .common import load_config
    lang = bible.get("language") or load_config().get("language", "hi")
    return "en" if lang == "en" else "hi"


def text(bible: dict, key: str) -> str:
    return TEXT[key]


# Art styles a story can pick with "art_style" (overrides the genre's look; grade/music stay).
ART_STYLES = {
    "cinematic": None,  # the genre's own film-still look (default)
    "creepy_comic": "creepy graphic novel illustration, bold black ink outlines, flat muted colors, "
                    "heavy shadows, unsettling expressions, horror comic panel, detailed background",
    "dark_fantasy": "dark fantasy digital painting, dramatic rim light, torchlight and deep shadows, "
                    "epic scale, painterly texture, ominous atmosphere",
    "painting": "oil painting, visible brush strokes, rich muted colors, dramatic chiaroscuro lighting, "
                "classical composition",
    "folk_myth": "Indian folk-myth illustration, ornate details, storm-lit sky, mythic and ancient, "
                 "painterly, dramatic lighting",
    "polaroid": "old faded polaroid photograph, flash photography, washed-out colors, light leaks, "
                "found-footage feel, slightly blurred",
}


def get(bible: dict) -> dict:
    g = bible.get("genre", DEFAULT)
    if g not in GENRES:
        raise ValueError(f"unknown genre '{g}'. Use one of: {', '.join(GENRES)}")
    out = {"name": g, **GENRES[g]}
    art = bible.get("art_style", "cinematic")
    if art not in ART_STYLES:
        raise ValueError(f"unknown art_style '{art}'. Use one of: {', '.join(ART_STYLES)}")
    if ART_STYLES[art]:
        extra = ", faces obscured or turned away, no identifiable people" if out.get("true_story") else ""
        out["style"] = ART_STYLES[art] + extra
    return out
