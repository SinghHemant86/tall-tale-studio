# Tall-Tale story rules

Claude follows these when you say **"lock it"**; the render checks the critical ones and refuses a
story that breaks them.

## Language
- **The channel is Hindi.** Default `language` is `hi`: every spoken line, the title, the thumbnail
  text, the cards and the description are in Hindi, written in **Devanagari**. No English line at all.
- Names and everyday English loanwords are also written in Devanagari (राघव, मानसून, सील, मोबाइल).
  The render rejects any Hindi story line containing Roman letters (digits like 1994 or 4-बी are fine).
- Never Roman Hindi (`Kaun hai andar`), never a line followed by its translation.
- Only image prompts (`setting`, `look`, `thumbnail.prompt`) stay in English; nobody sees them.
- Give a Hindi `logline_hi` (one or two sentences, no spoilers): it becomes the YouTube description if the free LLM is unavailable.
- An English-only story is possible with `"language": "en"` (then no Hindi lines).

## Pacing
- One idea per line; aim for 8–20 words. Lines over 40 words are rejected.
- The picture changes at least every ~3.5 s: long lines are split into several shots
  (wide → close-up → detail → low angle ...). A line may set `"shot"` (text or list) to direct
  its own framing.
- The first 15 seconds must hook: open on the strangest image or line in the story, not on setup.

## Thumbnail
- `"thumbnail": {"prompt": "...", "text": "..."}`
- `text`: **3 words max**, must not repeat the title (use `/yt-package` rules).
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
