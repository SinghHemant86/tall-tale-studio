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

Optional: start a filename with a mood (`dread_`, `chase_`, `calm_`...) and scenes with that
`"mood"` will prefer it. Without that, the first tracks in the folder are used in turn.
