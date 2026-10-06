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
DISCLAIMER_HI = "सच्ची घटनाओं पर आधारित।\nकुछ दृश्य नाटकीय रूप में दिखाए गए हैं और कुछ नाम बदल दिए गए हैं।"

# fixed on-screen / description text per language
TEXT = {
    "en": {"disclaimer": DISCLAIMER, "presents": "A TALL-TALE PRESENTATION", "thanks": "Thank you for listening",
           "subscribe": "Subscribe to Tall-Tale for the next story", "sources": "Sources are listed in the description",
           "sources_head": "Sources:",
           "footer": "Tall-Tale: thrillers, dark dramas, horror and true stories, narrated.\nVisuals and voices are AI-generated."},
    "hi": {"disclaimer": DISCLAIMER_HI, "presents": "एक टॉल-टेल प्रस्तुति", "thanks": "सुनने के लिए धन्यवाद",
           "subscribe": "अगली कहानी के लिए टॉल-टेल को सब्सक्राइब करें", "sources": "स्रोत विवरण में दिए गए हैं",
           "sources_head": "स्रोत:",
           "footer": "टॉल-टेल: थ्रिलर, डार्क ड्रामा, हॉरर और सच्ची घटनाओं की कहानियाँ।\nदृश्य और आवाज़ें AI से बनाई गई हैं।"},
}


def language(bible: dict) -> str:
    """'hi' (channel default) or 'en'. 'hinglish' is no longer used: a story is all Hindi or all English."""
    from .common import load_config
    lang = bible.get("language") or load_config().get("language", "hi")
    return "en" if lang == "en" else "hi"


def text(bible: dict, key: str) -> str:
    return TEXT[language(bible)][key]


def get(bible: dict) -> dict:
    g = bible.get("genre", DEFAULT)
    if g not in GENRES:
        raise ValueError(f"unknown genre '{g}'. Use one of: {', '.join(GENRES)}")
    return {"name": g, **GENRES[g]}
