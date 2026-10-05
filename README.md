# Tall-Tale Studio

The production line behind the **Tall-Tale** YouTube channel: thrillers, dark psychological
thrillers, dark dramas, horror and true incidents. A locked story becomes a finished, branded
YouTube video every day, laptop off. Total cost: ₹0.

```
 chat with Claude ──"lock it"──▶ queue/xxx.json ──(daily 06:47 IST, GitHub Actions)──▶
   character portraits → scene images → voices → Ken Burns motion + grade → music + SFX
   → Tall-Tale intro + end cards → subtitles → final mp4 + thumbnail → YouTube (private) → done/
```

| Stage | Engine (free) |
|---|---|
| Story, characters, dialogue | Claude, in chat — you decide, then "lock it" |
| Images | Cloudflare Workers AI (FLUX.1 schnell, free 10k neurons/day), fixed seed per character |
| Voices | Edge-TTS (Microsoft neural voices, Hindi + Indian English) |
| Motion | ffmpeg zoom/pan, vignette, film grain, fades |
| Music / SFX | Your Pixabay downloads in `music/` and `sfx/`, auto-ducked under voices |
| Titles, descriptions | Free LLMs with fallback: OpenRouter → Gemini → Groq |
| Upload | YouTube Data API (free quota), uploaded as **private** |

## Workflow

1. **Develop** the story with Claude in chat.
2. **"lock it"** → Claude gives you the story file (`queue/NNN-slug.json`). Commit it to the repo
   (GitHub web: *Add file → Upload files* into `queue/`). Lock several at once to build a buffer.
3. **Daily** the workflow renders the oldest story and uploads it as private. You review on
   YouTube Studio and publish or schedule it.
4. **"go"** = render now: set `"priority": true` in the file, then *Actions → Tall-Tale daily render →
   Run workflow*.

Each run's video, thumbnail and character portraits are also downloadable from the run page for 14 days.

## One-time setup (~30 min)

1. **Create the repo** under your GitHub account and push this folder. Public repos get unlimited
   Actions minutes; private repos get the free monthly allowance (enough for one video a day).
2. **Free API keys** (add each under repo *Settings → Secrets and variables → Actions*):
   - `OPENROUTER_API_KEY` — openrouter.ai (no card needed)
   - `GEMINI_API_KEY` — aistudio.google.com (optional fallback)
   - `GROQ_API_KEY` — console.groq.com (optional fallback)
   - `CF_ACCOUNT_ID` and `CF_API_TOKEN` — Cloudflare (free): images. Token template "Workers AI"
3. **YouTube upload**: follow the steps at the top of `scripts/get_youtube_token.py`, run it once on
   your laptop, and add `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` as secrets.
4. **Music**: drop Pixabay tracks into `music/` named `<mood>_name.mp3` (see `music/README.md`).
5. **Test**: *Actions → Tall-Tale daily render → Run workflow* with upload unticked. Download the result.

## Run on the laptop (Windows)

```powershell
winget install Gyan.FFmpeg
py -m venv .venv; .venv\Scripts\activate
pip install -r requirements.txt
python run.py --no-upload --keep-in-queue      # real images + voices, no upload
python run.py --offline --keep-in-queue        # placeholder images/voices, tests ffmpeg only
```

## Genres

Set `"genre"` in the story file. Each one has its own visual style, colour grade, narrator delivery
and default music mood (edit them in `studio/genres.py`):

| genre | look | default music mood |
|---|---|---|
| `horror` | fog, deep shadows, desaturated | `dread` |
| `thriller` | cold blue-grey, hard contrast | `pulse` |
| `psychological` | unsettling symmetry, close-ups, sickly tones | `drone` |
| `dark_drama` | warm but faded, window light | `piano` |
| `true_incident` | documentary, archival look, faces obscured | `ambient` |

### True incidents

- The story file must include `"sources": ["https://…", …]`; the render refuses to start without them.
- A "Based on true events" card plays after the intro, and the sources go in the video description.
- Mark real people with `"real": true`. They get no portrait and appear only as faceless silhouettes.
- Keep violence off screen and out of detailed narration; tell what happened and why it matters.

## Branding

`assets/logo.png` (the Tall-Tale emblem) is used for the intro card, end card and thumbnail corner.
Card lengths and on/off switches are under `branding:` in `config.yaml`. Name music files
`intro_*.mp3` and `outro_*.mp3` to give the cards their own sting.

## Story file format

See `queue/001-the-last-tenant.json`. Key fields:

- `genre`: see the table above; `sources` for true incidents; optional `narrator_voice`
- `characters[]`: `id`, `name`, `look` (repeated verbatim in every image prompt), `voice`
  (Edge-TTS voice), optional `rate`, `pitch`, `seed`, `real`
- `scenes[]`: `setting`, `characters` present, `mood` (picks music), `motion`
  (`zoom_in`, `zoom_in_fast`, `zoom_out`, `pan_left`, `pan_right`, `drift_up`), optional `sfx`,
  optional `image_prompt` to override, and `lines[]` of `{speaker, text}` (`narrator` or a character id)

Voices worth trying: `hi-IN-MadhurNeural`, `hi-IN-SwaraNeural`, `en-IN-PrabhatNeural`,
`en-IN-NeerjaNeural`, `en-GB-RyanNeural`. Full list: `edge-tts --list-voices`.

## Notes

- Uploads are marked as containing synthetic (AI) media, as YouTube requires.
- Custom thumbnails only apply once the channel is phone-verified.
- Free model names on OpenRouter rotate; if titles stop generating, update `llm.providers` in `config.yaml`.
- Pollinations and Edge-TTS are free community/public endpoints with no uptime guarantee; the
  pipeline retries with backoff, and a failed run leaves the story in the queue for the next day.
