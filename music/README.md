# Background music

Drop your Pixabay downloads here, named by mood so each scene picks the right one:

    dread_dark-ambient-01.mp3
    dread_haunted-house.mp3
    chase_heartbeat-tension.mp3
    calm_eerie-piano.mp3
    reveal_horror-sting.mp3
    intro_tall-tale-sting.mp3
    outro_soft-strings.mp3

Genres pick a default mood (horror `dread`, thriller `pulse`, psychological `drone`,
dark drama `piano`, true incident `ambient`), and a scene's own `mood` overrides it.
A scene with `"mood": "chase"` uses the first `chase_*` file. If none matches, any track is used;
if the folder is empty, a synthetic low drone is generated so renders never fail.
Mood names are free text — just keep them consistent between story files and file names.
