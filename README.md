# ORBIT – promotional video kit

Everything needed to produce the 60-second promo for **ORBIT – Educational & Tourism
Space Center**: generation prompts, synchronized Arabic subtitles, brand assets, and a
script that assembles the final 4K film.

The photorealistic footage, the narrator's voice and the score are not in this
repository; they have to be generated or recorded from `prompts/production-brief.md`
and dropped into `clips/` and `audio/`. Until they are, the build substitutes labelled
placeholders so the edit, titles and subtitles can be reviewed.

## Workflow

1. Generate the 11 clips, 8 narration lines and the music track described in
   [`prompts/production-brief.md`](prompts/production-brief.md).
2. Save them as `clips/s1.mp4 … s6.mp4`, `audio/vo/01.wav … 08.wav`, `audio/music.wav`.
3. Build:

```sh
python3 build.py --list       # clip checklist with required lengths
python3 build.py --preview    # fast 1080p render -> out/orbit_promo_preview.mp4
python3 build.py              # final 3840x2160 -> out/orbit_promo_4k.mp4
python3 build.py --no-subs    # branding only; ship subtitles/orbit_ar.srt as a sidecar
```

Requires Python 3 and ffmpeg built with libass. The build warns about any missing or
too-short asset and about narration lines that run into the next one.

## What the build does

- Fits every clip to its storyboard slot at 24 fps, 16:9, with 0.5 s crossfades; output
  is exactly 60 s (1440 frames).
- Burns in the Arabic subtitles (IBM Plex Sans Arabic, white with soft dark outline,
  bottom centre, right-to-left), the scene 3 title, the zone captions and the end card
  with the orbit logo and tagline.
- Places each narration line at its cue time, keeps the music below the voice and ducks
  it further while the narrator speaks.

## Timeline

Scene boundaries follow the storyboard. Narration lines 6 and 7 start slightly before
their scene cut: the closing sentence and tagline need about 13 s at a documentary pace,
which does not fit inside the final 10 s scene.

| Scene | Picture | Narration cues |
|---|---|---|
| 1 The wonder of space | 0–8 s | 1.5–7.2 |
| 2 The problem | 8–15 s | 8.3–14.7 |
| 3 Introducing ORBIT | 15–23 s | 15.6–22.4 |
| 4 Explore the universe (5 zones) | 23–40 s | 23.4–29.6, 30.4–36.2 |
| 5 Technology meets education | 40–50 s | 39.4–45.2 |
| 6 Vision and final branding | 50–60 s | 46.4–55.2, 56.0–59.6 |

To retime, edit `SHOTS` and `CUES` at the top of `build.py`; the subtitle files in
`subtitles/` are regenerated on every build (`--subs-only` to regenerate without
rendering).

## Layout

```
build.py                     timeline + assembly
prompts/production-brief.md  video, narration and music prompts
subtitles/orbit_ar.srt       Arabic subtitles (sidecar)
subtitles/orbit_en.srt       English narration transcript
subtitles/orbit_burnin.ass   styled subtitles + branding used for burn-in
assets/brand/orbit-logo.svg  logo mark
assets/fonts/                IBM Plex Sans Arabic, Michroma (SIL OFL)
clips/, audio/               your generated media (git-ignored)
```
