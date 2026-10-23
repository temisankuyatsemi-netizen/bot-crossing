# Bot Crossing

A live 3D voxel world where Ninja Turtle bots build out your empire.

## The Crew

| Bot | Bandana | Sector |
|-----|---------|--------|
| Leonardo | 🔵 Blue | Content Hub (TikTok / YouTube) |
| Donatello | 🟣 Purple | Stocked (invention & product) |
| Raphael | 🔴 Red | Athletic Wear (personal brand) |
| Michelangelo | 🟠 Orange | Creative Collective (art & culture) |
| Splinter | 🟢 Green | HQ / Ops (strategy) |

## Running locally

Open `index.html` directly in a browser — no build step needed. Three.js loads from CDN.

## Updating

The live version lives at: https://claude.ai/artifact/Fxepg187UParx7vBNqKfxN

To push changes: edit `index.html`, commit, push to `main`. Paste the updated file back into Claude to republish the artifact.

## Structure

- `index.html` — the entire world (Three.js scene, bot logic, HUD overlay, sector data)

Each sector's tasks are defined in the `SECTORS` array near the top of the script block — easy to edit.

## Video editing with Claude Code

`.claude/skills/video-edit/` is a skill for the Content Hub. Ask Claude Code to "edit my video" (or type `/video-edit`) and it runs six steps: hook and script, silence cutting, design plan, a parallel build with subagents (captions, graphics, B-roll, thumbnail), QA by the `video-checker` agent, and saving your feedback to `NOTES.md` so later edits follow it.

- Needs `ffmpeg`. Captions also need `pip install faster-whisper`.
- Fill in `.claude/skills/video-edit/style.md` with your brand once.
- Footage goes in `videos/<slug>/raw/`. The `videos/` folder is git-ignored.
