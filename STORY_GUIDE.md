# Tall-Tale story rules

Claude follows these when you say **"lock it"**; the render checks the critical ones and refuses a
story that breaks them.

## Language
- **Audio is Hindi; everything written is English.** Narration and dialogue are Hindi in
  **Devanagari** (names and loanwords too: राघव, मानसून). The title, description, tags, hashtags,
  subtitles and the intro/end cards are English. Only the **thumbnail text** may be Hindi.
- Every Hindi line carries `"en"`: its English translation, shown as the subtitle. Written by
  Claude when the story is locked, not machine-translated at render time.
- Never Roman Hindi in a spoken line (`Kaun hai andar`), never a line followed by its translation.
- Image prompts (`setting`, `look`, `thumbnail.prompt`) are English; nobody sees them.
- The render refuses a story that breaks these rules.

## Search (SEO), written when the story is locked
- `title`: English, under ~60 characters, the hook first, then `| Hindi Horror Story` (or the genre).
- `youtube.description`: 2-3 English sentences, the most searchable phrase in the first sentence,
  no spoilers. The render adds the AI-disclosure line, sources (true incidents) and hashtags.
- `youtube.hashtags`: 1-2 story-specific ones (place, theme), e.g. `#HauntedHaveli`. The render adds
  the genre's and `#TallTale`; YouTube shows the first three above the title.
- `youtube.tags`: 5-8 English phrases a viewer would type, specific to this story (setting, creature,
  situation). Genre and channel tags are added automatically; any geography, only if the story has one.

## Pacing
- One idea per line; aim for 8–20 words. Lines over 40 words are rejected.
- The picture changes at least every ~3.5 s: long lines are split into several shots
  (wide → close-up → detail → low angle ...). A line may set `"shot"` (text or list) to direct
  its own framing.
- The first 15 seconds must hook: open on the strangest image or line in the story, not on setup.

## Thumbnail
- `"thumbnail": {"prompt": "...", "text": "..."}`
- `text`: **3 words max**, Hindi allowed (e.g. `कौन है अंदर?`), must not repeat the title (use `/yt-package` rules).
- `prompt`: one subject, close, high contrast, dark empty space on the left for the text.

## True incidents
- `"sources"` with links is required; real people get `"real": true` (faceless only).

## Voices (ElevenLabs)
- Narrator voice ID lives in `config.yaml` (`voice.elevenlabs.narrator`); a story may override with
  `"narrator_eleven"`.
- Each character gets a `"role"` from the cast in `config.yaml` (old_man, friend, young_man, woman,
  young_woman, child, ghost, villain, officer), or a specific `"eleven_voice": "<voice id>"`,
  plus optional `"eleven_settings"`
  (`stability` lower = more emotional, `style` higher = more dramatic). `"gender"` picks the default.
- If the month's ElevenLabs characters can't cover the whole story, the story uses the free voices
  instead (never a mix inside one video).

## Look
- Hands are welcome, close-ups included. For ghosts and other supernatural characters, write the
  wrongness into the `look`: long, bony, twisted or too-many-jointed fingers, grey skin, cracked
  nails. Living humans get normal hands.
