# Claude Code skills

Custom [Claude Code](https://claude.com/claude-code) skills.

| Skill | What it does |
| --- | --- |
| [`blender-game-artist`](blender-game-artist/SKILL.md) | Senior Blender environment and prop artist for Roblox games: reference-first modelling, texturing, baking, UVs and Roblox export. |
| [`roblox-ui-designer`](roblox-ui-designer/SKILL.md) | Senior game UI/UX designer for Roblox: designs in Figma, then imports into Studio as real GUI instances, with motion and review passes. |

## Install

Copy a skill folder into `~/.claude/skills/` (all projects) or `.claude/skills/` inside a project:

```bash
git clone https://github.com/kapscripts/claude-skills.git
cp -r claude-skills/roblox-ui-designer ~/.claude/skills/
```

Claude Code picks up the skill automatically; invoke it by describing the task or with `/roblox-ui-designer`.
