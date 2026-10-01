# Figma → Roblox pipeline

Design in Figma, approve there, import as real instances. This file is the full procedure.

## 1. Connect Figma (once per machine)

- **What's already there:** Figma desktop is installed on this machine (`AppData\Local\Figma`). The Roblox Studio MCP
  already has `upload_image`, which takes http(s) image URLs, Figma MCP asset URLs included.
- **Install the official Figma MCP (recommended):**
  - In a terminal: `claude plugin install figma@claude-plugins-official`. This bundles the MCP and Figma's own
    skills (`figma-use`, `figma-generate-design`, `figma-generate-library`).
  - Or directly: `claude mcp add --transport http figma https://mcp.figma.com/mcp --scope user`.
  - Authenticate: `/mcp`, choose figma, Authenticate, and approve in the browser. The user does this; never handle their
    password.
- **Check the seat:** call `whoami`.
  - Writing to the canvas (`use_figma`, `create_new_file`, `upload_assets`) needs a **Full seat** with edit access.
  - Dev and View seats are read-only.
  - Read tools are rate-limited by plan (Starter ≈ 6 calls a month; Pro 200 a day), so batch reads.
- **No Full seat?** Use a local-plugin bridge. The user must approve installing it.
  - **grab/cursor-talk-to-figma-mcp:**
    - Needs Bun: `bun setup`, then `bun socket`.
    - Install the "Talk to Figma" plugin in Figma.
    - MCP entry: `{"command":"bunx","args":["cursor-talk-to-figma-mcp@latest"]}`.
    - Tools: create_frame, create_text, set_fill_color, set_corner_radius, auto-layout, export_node_as_image.
  - **southleft/figma-console-mcp:** the Desktop Bridge plugin gives full Plugin API access.
- **Desktop Dev Mode MCP** (`http://127.0.0.1:3845/mcp`) is read-only, so it's only useful for importing existing designs.
- **If none of this is connected:** stop and tell the user the exact command. Never quietly build in Studio instead.
  Figma-first is the rule.

## 2. Design for Roblox (in Figma)

**Frames**
- **PC and console:** a 1920×1080 reference frame.
- **Phone:** an 844×390 landscape frame.
  - Check that touch targets and text still hold at phone scale. After UIScale the phone is about 0.36× the 1080p frame,
    so design phone-critical elements larger or give the phone its own layout.
- **Top bar:** add a 58 px guide for Roblox's top bar.
- **Bottom corners:** add guides for the phone thumbstick (bottom-left) and jump button (bottom-right).

**Structure**
- Use **auto layout** for anything list-like. It maps 1:1 to UIListLayout, UIPadding and UIFlexItem.
- Use constraints (Left, Right, Center, Left & Right, Scale) for edge-anchored HUD elements. They map to AnchorPoint and
  Scale/Offset.
- Components and variants for every state: Default, Hover, Pressed, Focused (gamepad), Disabled, plus Loading/Empty/Error
  for data views.

**Only use what Roblox can render natively**

| Figma feature | Roblox equivalent |
|---|---|
| Solid fills; one fill per layer (stack layers for more) | Background colour |
| Linear gradients (≤ 20 stops) | UIGradient; radial/conical are Studio beta only, so bake them |
| Corner radius, including per-corner | UICorner |
| Stroke (inside/center/outside) | UIStroke |
| Drop shadow | UIShadow; keep ≤ ~100 on screen |
| Text in Roblox-available fonts (see below) | TextLabel with FontFace |
| Line height | TextLabel.LineHeight |
| Uppercase | textCase |

**Anything else gets baked into an image:** name the layer `…_img`. That covers:
- layer or background blur;
- blend modes;
- inner shadows;
- radial/angular gradients;
- letter-spacing-critical titles;
- textures and grain;
- illustrations;
- custom lettering.

Keep baked images small (≤ 1024², icons 64–128 px at @2x). Use 9-slice for resizable panels: record the slice insets,
and the builder supports `node.slice`.

**Fonts**
- Roblox can't upload custom fonts, so pick from Roblox's library.
- Good tactical/industrial families:
  - **Display / headings:** Oswald, Michroma, Sarpanch
  - **Labels:** Roboto Condensed, Titillium Web, Jura
  - **Numbers:** Roboto Mono, Special Elite (for stencil flavour)
  - **Body:** Builder Sans, Montserrat
- Anything else maps to Builder Sans with a warning, or gets baked.

**Layer naming**

| Suffix | Becomes |
|---|---|
| `_btn` | TextButton / ImageButton |
| `_scroll` | ScrollingFrame |
| `_img` | baked PNG |
| `_ignore` | skipped (guides, notes) |

Give every other layer a meaningful name: it becomes the Instance name that code looks up.

**Icons:** Lucide only (24-px grid). Fetch `https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/<name>.svg`. In
`use_figma`, call `figma.createNodeFromSvg(svg)`, clear the frame fill, and set each child's strokes to the palette
colour. Use one strokeWeight per display size (about 2 × size / 24, and heavier for hero icons at 140 px, where 6.5
worked), with round caps and joins. Name it `Icon_<name>_img` and keep the source copies on the canvas as
`Lucide_<name>_ignore`. Export them white and tint in Roblox with ImageColor3.

## 3. Review in Figma

- `get_screenshot` each frame (desktop and phone) and show the user.
- Iterate in Figma until they approve. No Studio work before approval.

## 4. Export and upload images

1. Export every `_img` layer and image fill at @2x:
   - Figma MCP `download_assets`, or `export_node_as_image` with Talk-to-Figma;
   - or REST `GET /v1/images/:key?ids=…&scale=2&format=png`, with a personal access token kept in an env var and never
     printed.
2. Upload with Studio MCP `upload_image`, which takes a list of http(s) URLs and returns `rbxassetid://`.
   - Or use Open Cloud `POST https://apis.roblox.com/assets/v1/assets` (API key with `asset:write`; poll the operation).
   - Or Studio's Asset Manager bulk import.
3. Cache by content hash so the same image never uploads twice.
4. Write `assets.json`: `{"<figma node id>": "rbxassetid://…"}`.

## 5. Import

1. **Walk the frame with `use_figma`.** Paste `scripts/figma_walker.js` with `__ROOT_ID__` set to the frame id (URL
   `node-id=12-345` becomes `12:345`) and `__PAGE__` = 0, 1, 2… until `done` is true. Save each `data` string to
   `page0.txt`, `page1.txt` and so on.
   - Output is capped at about 20 KB per call, hence the paging.
   - The Plugin API is async-safe (`getNodeByIdAsync`). If the `use_figma` wrapper needs a different return style,
     adapt only the last lines.
   - REST alternative: `GET /v1/files/:key/nodes?ids=…`, then `--rest nodes.json --node 12:345`.
2. **Generate the Luau:**
   `python scripts/figma_to_luau.py --pages page0.txt page1.txt --assets assets.json --screengui --name LootScreen --out build.lua`
3. **Preview first.** Run `build.lua` through Studio MCP `execute_luau` with the default `--parent nil`. That gives a
   detached build and a report of instance count and warnings (fonts swapped, effects that need baking, rotated layers,
   absolute children in auto layout). Fix the design or accept the warnings.
4. **Import for real only when the user has approved this screen** (Rule 0). Re-run with
   `--parent game.StarterGui` (or the project's UI folder) and a staging name, then swap it into place. Sync to every
   place that uses it.
5. **Scaling:** by default the root frame is the Figma size with a `DesignScale` UIScale. Call
   `UIMotion.fitDesignScale(root)` from the client so it fits any screen (min of the viewport/design ratios).
   `--no-scale-root` builds a full-screen Scale root instead.

## 6. Verify

- Run Studio's Device emulator at phone (844×390), tablet, 1080p, 1440p, 4K and console.
- Compare with the Figma screenshot: layout, text wrapping, safe areas, gamepad navigation (NextSelection…,
  SelectionImageObject), touch-target size.
- Fix in one batch and confirm once. Anything that can't be matched natively goes back to Figma as `_img`.

## Mapping reference (what the builder does)

| Figma | Roblox |
|---|---|
| Frame / Rectangle | Frame (a group with opacity < 1 becomes a CanvasGroup) |
| Auto layout H/V, gap, padding | UIListLayout FillDirection + Padding, UIPadding |
| Space-between / wrap | HorizontalFlex/VerticalFlex = SpaceBetween, `Wraps` |
| Child "Fill container" | UIFlexItem FlexMode Fill (main axis), Scale 1 (cross axis) |
| Hug contents | AutomaticSize |
| Constraints L/R/C/L&R/Scale | AnchorPoint + UDim2 Offset/Scale |
| Corner radius / per-corner | UICorner CornerRadius / TopLeftRadius… |
| Stroke inside/center/outside | UIStroke BorderStrokePosition Inner/Center/Outer (Contextual for text) |
| Linear gradient | white background + UIGradient Color/Transparency sequences + Rotation |
| Drop shadow | UIShadow (BlurRadius UDim, Offset UDim2, Spread UDim2) |
| Text | TextLabel: FontFace (family + weight + italic), TextSize, LineHeight, alignment, uppercase |
| Image fill / `_img` | ImageLabel (ScaleType Crop/Fit/Tile/Stretch/Slice) |
| Clip content | ClipsDescendants (doesn't clip to rounded corners; use a CanvasGroup for that) |

**Known losses** (all reported as warnings):
- letter spacing;
- blur;
- blend modes;
- inner shadow;
- multiple fills;
- radial gradients;
- absolute children inside auto layout;
- rotation pivot, since Roblox rotates about the centre.

## Off-the-shelf alternatives (only if the user prefers them)

- **FigBloxUI** (paid, most complete): auto layout, 9-slice, auto-upload of images.
- **RoImport** (free): layer-prefix based, with a bridge app.

Neither is needed. The scripts here keep the pipeline in our control.
