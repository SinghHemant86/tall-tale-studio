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
- Each character gets a `"role"` from the cast in `config.yaml` (old_man, elder, authority, friend, young_man, woman, child_girl, child_boy,
  young_woman, child, ghost, villain, officer), or a specific `"eleven_voice": "<voice id>"`,
  plus optional `"eleven_settings"`
  (`stability` lower = more emotional, `style` higher = more dramatic). `"gender"` picks the default.
- If the month's ElevenLabs characters can't cover the whole story, the story uses the free voices
  instead (never a mix inside one video).

## Look
- Scariness follows the story, not a rule. A ghost who should be frightening in that moment gets
  the wrongness written into the `look` (long, bony, twisted fingers, grey skin, cracked nails),
  close-ups and hands included.
- A ghost who is sad, gentle, or not yet revealed looks ordinary or simply pale; a story can stay
  quiet and real-looking and let the narration do the work. Decide per character, per scene.

## Real people and real cases
- Report, never conclude. State the official position first and clearly (court, police, CBI), then any
  claims, labelled as claims with who made them ("the family alleged", "a staff member told a news
  channel"). No verdict of our own.
- Never name or hint at a living person as guilty of anything a court has not convicted them of,
  even "as per reports" (repeating an accusation is still the accusation).
- No private or medical details beyond what official records made public; no body or surgery talk.
- Sources: official records and established news outlets only, listed in the description.
- Title and thumbnail ask questions, they do not answer them ("What the CBI found, and what is still
  asked"), never "MURDER EXPOSED". Real people stay faceless or stylised, never photo-real.
- Expect limited ads on real deaths; that is the price of the topic.

## Shorts (trailer-style, from the long video)
- `"shorts": [{"scenes": ["s2", "s3"], "title": "English hook title", "hook": "image prompt"}, ...]`,
  3-4 per long video. `hook` = the most striking picture in the story, shown first (optional).
- Sound: the long video's own narration and music for those scenes (no extra voice credits).
- Picture: new square images every ~1.5 s (close-ups, eyes, hands, objects) with fast push-ins,
  shakes and white flashes; captions pop in 3 words at a time; title on top; closing card
  "Watch the full story on Tall-Tale". About 20-35 new images per Short.
- Pick moments that work alone and end on a cliffhanger. Under a minute (trimmed at a line end).
- Uploaded to YouTube with "Full story ▶ <long video link>"; files kept in the run's download for Reels.

## Settings
- Prefer remote, lesser-known places (villages, hill hamlets, desert outposts, forest rest houses,
  closed railway stations), and rotate states from story to story. Avoid repeating big cities.
