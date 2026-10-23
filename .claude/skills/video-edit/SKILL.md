---
name: video-edit
description: Edit a video end to end without touching a timeline - write the hook and script, cut raw footage, plan the design, build captions and graphics with subagents, QA the render, and learn from feedback notes. Use when the user wants to script, cut, caption, edit, or package a YouTube video, TikTok, Short, or Reel, or hands over raw footage.
---

# Video edit

Six jobs, run in order. Each one produces a file in the project folder, so any
job can be redone without redoing the others. Work in a folder per video:
`videos/<slug>/` with the raw footage in `raw/`.

**Before anything else, read `NOTES.md` in this skill folder.** It holds what
the user liked and disliked in past edits. Apply every rule in it.

Requires `ffmpeg`. Captions also need `pip install faster-whisper`.
Scripts live in `.claude/skills/video-edit/scripts/` (shown below as `scripts/`).

## 1. Hooks and script → `script.md`

Ask for the topic, the audience, the platform (YouTube long-form, or 9:16
Shorts/TikTok/Reels) and the one thing a viewer should leave with.

- Write **5 hook options** for the first 3 seconds, each in a different style
  (bold claim, question, result-first, contrarian, story in motion). Each one
  is a single spoken line plus what's on screen. Let the user pick.
- Write the script as beats: `[0:00] HOOK`, then setup, 3-5 value beats,
  payoff, call to action. Keep one idea per beat. For shorts, aim for under 45s
  of speech (about 110 words).
- Mark where B-roll, text on screen, or zooms go: `[BROLL: ...]`, `[TEXT: ...]`.

If the user already recorded, skip this step and pull hooks from the footage
in step 2.

## 2. Cut the raw footage → `cut.mp4`, `cut.mp4.edl.json`

```bash
python3 scripts/silence_cut.py raw/take.mp4 cut.mp4
```

- Cuts pauses over 0.6s and keeps 0.12s around speech. Tune with
  `--noise -35` for a quiet room or `-25` for a noisy one, and with
  `--min-silence`. Use `--dry-run` to look at the EDL before rendering.
- Then transcribe the cut (`python3 scripts/transcribe.py cut.mp4`) and read
  the transcript for flubbed lines and retakes: when a sentence is said twice,
  keep the last clean take. Drop those ranges by editing the EDL's `keep`
  list and re-render with ffmpeg `trim`/`concat`, or tell the user the
  timestamps to drop.
- The first spoken line must be the hook. If the strongest moment is later,
  move it to the front.

## 3. Design → `design.md`

Read `style.md` in this skill folder for the user's fonts, colors and caption
look. If it still holds the placeholders, ask the user for their brand and
fill it in. Then write `design.md` covering:

- Format: 1920x1080 (16:9) or 1080x1920 (9:16).
- Caption style: words per line (3 for shorts, 6 for long-form), position,
  highlight color for key words.
- A shot list from the transcript timestamps: where each zoom, B-roll clip,
  text pop-up, sound effect and chapter title goes.
- Thumbnail concept: 3 options, each with at most 4 words of text.

Show the user `design.md` before building.

## 4. Build with subagents → `final.mp4`

Split the build into independent pieces and run them **in parallel** with the
Agent tool, each given `design.md`, the transcript and its output path:

| Subagent | Output |
|---|---|
| Captions | `captions.srt` or styled `captions.ass` (via `transcribe.py --max-words N`) |
| Graphics | Title cards and text pop-ups as PNG/MOV in `assets/` |
| B-roll | Clips trimmed and scaled to the format in `broll/` |
| Thumbnail | `thumbnail.png` at 1280x720 |

Then assemble in the main session. Typical final pass:

```bash
ffmpeg -i cut.mp4 -vf "subtitles=captions.srt:force_style='FontName=Inter,FontSize=18,Outline=2'" \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v libx264 -crf 18 -c:a aac final.mp4
```

For 9:16 from 16:9 footage, crop before the subtitles:
`-vf "crop=ih*9/16:ih,scale=1080:1920,subtitles=..."`.

## 5. Check the work

Run the technical check, then hand off to the `video-checker` agent:

```bash
python3 scripts/check.py final.mp4 --aspect 16:9
```

It reports black frames, leftover dead air, loudness (target -14 LUFS) and
clipping, and exits 1 if anything fails. The `video-checker` agent also reads
the captions against the script for typos and timing, and checks the hook
lands in the first 3 seconds. Fix everything it flags, then re-run both.

## 6. Learn from notes → `NOTES.md`

After the user reviews the edit, ask what they would change. Turn each piece
of feedback into a **short, general rule** (not about this one video) and
append it under the matching heading in `NOTES.md`, with the date. For
example "Cut was too tight in the intro" becomes "Use `--pad 0.2` for the
first 10 seconds". Replace rules the user contradicts instead of keeping both.

Finish by reporting the tokens and time the edit took, as the video does, so
the user can see what each edit costs.
