# Background music

One folder per genre, plus `intro` and `outro` for the Tall-Tale cards:

    music/
      horror/          psychological/     true_incident/     intro/
      thriller/        dark_drama/                            outro/

Drop Pixabay downloads into the folder of the genre they suit. No renaming needed.

- A horror story takes its music from `horror/`, a thriller from `thriller/`, and so on.
- The intro card uses `intro/`, the end card `outro/`.
- If a genre folder is empty, any track in `music/` is used; if there are none at all, a synthetic
  drone is generated so renders never fail.
- Tracks rotate scene by scene, so add a few per genre for variety. Longer tracks (2+ minutes) loop
  less noticeably.

## How tracks are chosen

Keep Pixabay's own filenames: words in the name set each track's role.
`opener`/`intro`/`logo` -> intro sting, `outro`/`ending`/`pad` -> end card,
`music-box`/`piano` -> calm moments, `trailer`/`chase`/`tense` -> chases and reveals,
`atmosphere`/`ambience`/`eerie`/`whisper`... -> dread (the default).

Each track is also measured: loudness every half second, its quiet and intense stretches, and
sudden hits. A calm scene gets the quietest stretch, a chase the loudest; the intro is timed so the
opener's hit lands as the logo appears; every track is levelled to the same loudness.
Results are cached in `library.json`. Run `python -m studio.music_lib` to see what was found.

Optional: start a filename with a mood (`dread_`, `chase_`, `calm_`...) and scenes with that
`"mood"` will prefer it. Without that, the first tracks in the folder are used in turn.
