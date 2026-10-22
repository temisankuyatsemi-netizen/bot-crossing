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
