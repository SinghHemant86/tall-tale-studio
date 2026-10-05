# Tall-Tale story rules

Claude follows these when you say **"lock it"**; the render checks the critical ones and refuses a
story that breaks them.

## Language
- Every line is in **one language**. Never say a line and then its translation
  ("कौन है अंदर? Who is in there?" is wrong).
- Hindi is written in **Devanagari** (`कौन है अंदर?`), never Roman Hindi (`Kaun hai andar`).
  Devanagari lines are automatically spoken by a Hindi voice, English lines by an English one.
- Story `language`: `en`, `hi`, or `hinglish` (mix allowed **between** lines, never inside one).

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
