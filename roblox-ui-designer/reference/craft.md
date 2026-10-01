# Craft: designing Roblox UI that looks authored, not generated

## 1. Shape before pixels

Answer these in a few lines before opening Figma. Use AskUserQuestion for anything that would change the work, 2–3
questions at most:

- **Player task:** what the player is trying to do on this screen, how often, and under what pressure (mid-fight HUD,
  post-raid inventory, first-time shop).
- **Information:** what they must see at a glance, what on demand, and what never.
- **Priority order:** rank it; the top item becomes the focal element.
- **States:** default, loading, empty, error, full or overflow, disabled, first-time. For the HUD also low health, no
  ammo, downed, spectating.
- **Platforms and input:** PC mouse/keyboard, phone touch, console gamepad, VR. Name the one that's hardest.
- **Constraints:** existing design system, project rules (no-UI-change rules), performance budget, localisation.
- **What must not change,** and what would make a polished result feel wrong.

Then list **5 structural options** (topology, not colours). Pick one, and say why it serves the task better than the
category default.

## 2. Find the visual world (the anti-AI step)

AI and template UIs cluster on a few looks, whatever the subject: dark with a neon accent and glow; purple→cyan
gradients with glass; rounded cards with soft shadows; a cartoon bubble font. If someone could guess your screen's look
from the genre alone, rework it.

1. **Name the game's fiction in one sentence,** plus the player's physical scene. For example: "ARC Raiders-style
   extraction: scavenging a ruined, sun-bleached Italian coast under hostile machines; raiders carry salvaged,
   hand-labelled field gear."
2. **List 7 concrete artefacts from that world** the UI could borrow a graphic language from. For the example above:
   - military field manuals and stencilled crate markings
   - ruggedised handheld terminals (bezels, segmented LCD digits)
   - hazard tape and warning placards
   - radio dials and signal meters
   - 1970s Italian transit and space-age signage (retro-futurist, off-white panels, condensed uppercase type)
   - duct-taped repairs and handwritten labels
   - topographic survey maps

   Make sure the list spans at least 3 material families.
3. **Pick one as the backbone** and let one other contribute a single discipline (for example the map's contour lines
   as a subtle texture).
4. **Write the direction** in five short blocks and get the user's OK in Figma:
   - **THESIS:** the one idea, and the default it refuses.
   - **WORLD:** palette roles, type roles, materials and shapes, recognisable with all text removed.
   - **HIERARCHY:** what leads each key screen.
   - **SIGNATURE:** one memorable interaction or moment (a stencil-wipe transition, an LCD tick-up for loot value).
   - **MOTION:** the vocabulary (mechanical snaps, shutters, scans), matching the fiction.

**Extraction-shooter conventions** (ARC Raiders, Tarkov, Hunt: Showdown):
- A minimal combat HUD: a compass with only key markers, health and shield, ammo only when it matters, contextual
  prompts instead of permanent buttons.
- Voice and sound carry information (pings with voice lines).
- Diegetic feedback where possible (suit displays, frost on the screen when cold).
- Loot UI flags tracked or needed items directly.
- The inventory is where players spend minutes: fast sorting and filtering, clear weight and slot limits, drag with
  forgiving targets. Hunt's 2024 UI backlash shows how much inventory UX matters.

## 3. What pros do (and AI doesn't)

- **Materials over effects.** Texture comes from authored images (9-slice panels with worn edges, grain, stencils), not
  gradients and glows.
- **One accent colour with meaning,** used rarely enough to pull the eye. Neutrals are tinted toward the world (warm
  sun-bleached greys, not pure #1E1E1E).
- **Rarity and state colours are a system** (Common grey, Uncommon green, Rare blue, Epic purple, Legendary gold, or the
  game's own), identical on every screen, and never the only cue: add shape, pattern or label.
- **Typography with character but discipline:** a condensed display face for headings and labels, a clean face for body,
  a monospaced or segmented face for numbers. Three families at most, clear weight steps.
- **Asymmetric, edge-anchored composition** and a real grid, not everything centred.
- **Icons from Lucide:** one set with one stroke and grid (lucide.dev, ISC; `lucide-static` SVGs on jsDelivr). Choose
  each icon for what it means on this screen, and swap freely when a better glyph exists. For currency tiers, show the
  currency icon as 1 → pair → pyramid, then give the top tier a different, bigger accent icon. Brand marks (such as
  Robux) and the game's own currency icon stay as they are. Draw a custom icon only when
  Lucide has nothing that fits, and match Lucide's 24-px grid and 2-px round stroke.
- **Consistency as convention:** the same close button everywhere (DOORS' square red X), the same premium marker
  (Jailbreak's gold stripe), the same health colour (Arcane Odyssey's green).
- **Diegetic, spatial and meta UI** where it adds immersion: damage vignettes, a suit display, world-space markers.
- **Sound on every meaningful state change** (real recordings, not synth blips).

## 4. Type, colour and layout rules

**Typography**
- **Roles:** display (titles, reveals), heading, body, label (uppercase, tracked via font choice since Roblox has no
  letter spacing), numeric.
- **Sizes at 1080p:**
  - body 16–20, label 12–14, heading 24–32, display 40–72;
  - console/TV body 24–28;
  - never below 12 on PC or 16 effective on phone.
- **Line height:** 1.1–1.25 for headings, 1.3–1.5 for body (`TextLabel.LineHeight`).
- Light text on dark needs one weight step more and slightly more line height.
- **Fixed TextSize per role** with one UIScale for the whole ScreenGui. TextScaled only for single isolated words in a
  fixed box, never next to other text.
- **Localisation:** allow +40% width. Use AutomaticSize and wrapping; no text baked into images except logos.

**Colour**
- **Build roles, not swatches:**
  - canvas and panels (2–3 elevation steps);
  - text primary and secondary (secondary text is derived from the surface hue, never plain grey on colour);
  - accent (action, focus, selection);
  - border;
  - semantic (success, warning, danger, info);
  - rarity.
- **Contrast:** 4.5:1 for body text, 3:1 for large text, icons and focus indicators. Text over the 3D world needs a scrim,
  UIStroke (Contextual) or UIShadow.
- **Tokens:** define them once in a StyleSheet (StyleRule tokens) so themes and colour-blind modes remap roles.

**Layout**
- **4-px spacing scale:** 4, 8, 12, 16, 24, 32, 48, 64.
- Group by proximity before adding containers. No card-inside-card.
- **Squint test:** blur the screen; the primary element, the secondary element and the groups must still read in order.
- **Density follows task frequency:** the inventory can be dense, a reward screen is sparse and dramatic.
- Edge-anchor HUD elements with AnchorPoints (0,0 / 1,0 / 0,1 / 1,1) and consistent margins (24–32 px at 1080p).

## 5. Roblox technical rules

- **ScreenGui settings:**
  - `ResetOnSpawn = false` for persistent UI.
  - `ZIndexBehavior = Sibling`.
  - `ScreenInsets = CoreUISafeInsets` (keeps clear of the 58 px top bar), or `DeviceSafeInsets` plus your own margins for
    notches.
  - `GuiService.TopbarInset` is a Rect you can listen to. `GetGuiInset()` returns 0 on the first frame, so wait a Heartbeat.
- **Sizing strategy:**
  - Author in Offset at the Figma reference size, with one UIScale fitted to the viewport (`UIMotion.fitDesignScale`).
  - Use Scale only for full-bleed backgrounds and splits.
  - UIAspectRatioConstraint for fixed-ratio elements; UISizeConstraint for min/max.
  - AutomaticSize for text, lists and tooltips. Don't combine it with TextScaled.
- **Layouts:**
  - UIListLayout: FillDirection, Padding, alignment, `Wraps`, `HorizontalFlex`/`VerticalFlex` (Fill / SpaceBetween /
    SpaceAround / SpaceEvenly), `ItemLineAlignment`.
  - UIFlexItem: Grow / Shrink / Fill / Custom ratios.
  - UIGridLayout for uniform grids. UIPageLayout for pagers.
- **Styling objects:**
  - **UICorner:** CornerRadius, plus TopLeftRadius / TopRightRadius / BottomRightRadius / BottomLeftRadius.
  - **UIStroke:** Thickness, Color, Transparency, `ApplyStrokeMode` (Contextual for text, Border for frames),
    `BorderStrokePosition` (Outer / Center / Inner), `StrokeSizingMode` (FixedSize / ScaledSize), `BorderOffset`,
    LineJoinMode. Keep it under ~300 on screen. ScaledSize ignores UIScale.
  - **UIShadow:** BlurRadius (UDim), Offset (UDim2), Spread (UDim2), Color, Transparency, negative ZIndex. Keep it under
    ~100. It shadows the rectangle, not text.
  - **UIGradient:** linear, ≤ 20 keypoints, multiplies the base colour (set the base to white). Radial, conical and tiled
    gradients are in Studio beta (Sept 2026) and can't be published yet.
  - **9-slice:** `ScaleType.Slice`, `SliceCenter` (in source pixels), `SliceScale` (0.5 for @2x art).
- **StyleSheet system (live since 2026):**
  - StyleSheet, StyleRule and StyleLink hold tokens and themes.
  - StyleQuery adds conditions: `@ViewportDisplaySizeSmall/Medium/Large`, `@PreferredInputTouch/Gamepad/KeyboardAndMouse`,
    ReducedMotionEnabled, PreferredTextSize.
  - Styling Transitions run native state animations.
  - Use it for anything with many instances of one style.
- **Fonts:**
  - `Font.new("rbxasset://fonts/families/X.json", weight, style)`, `Font.fromEnum`, `Font.fromName`, `Font.fromId`.
  - No custom font uploads, so bake unusual lettering.
  - Families that exist in the engine (checked live): BuilderSans, Montserrat, Oswald, Michroma, Roboto, RobotoCondensed,
    RobotoMono, TitilliumWeb, Jura, Sarpanch, SpecialElite, Arimo and more.
  - Gotham and Arial were removed; they map to Montserrat and Arimo.
- **Rich text:** `<b> <i> <u> <s> <br/> <uc> <sc> <font color size face family weight transparency> <stroke> <mark>`.
  There is no letter spacing.
- **Images:**
  - Uploads are capped at 1024² decals.
  - Upload icons white and tint with ImageColor3.
  - Pack atlases with ImageRectOffset/ImageRectSize.
  - `ResampleMode = Pixelated` for pixel art.
- **Interaction:**
  - GuiButton with `AutoButtonColor = false` and your own states.
  - UIDragDetector for drag and drop (DragStyle, BoundingUI).
  - ProximityPrompt (with a custom style) for world interactions.
  - Path2D for vector lines.

## 6. Cross-platform (adapt)

- **Phone:**
  - Touch targets ≥ 44–48 px effective after scaling, ≥ 8 px apart.
  - Roblox's thumbstick is bottom-left and jump is bottom-right (70 px controls on small screens, 120/90 px otherwise);
    place action buttons around jump.
  - Keep the top 58 px clear.
  - Make phone-critical UI bigger, or give the phone its own layout via StyleQuery `@ViewportDisplaySizeSmall`.
- **Console / TV (10-foot):**
  - Body text ≥ 24–28 px at 1080p.
  - Every screen has a default `GuiService.SelectedObject` (via `GuiService:Select(parent)` + SelectionOrder), explicit
    `NextSelectionUp/Down/Left/Right` where the automatic choice is wrong, and `SelectionGroup` +
    `SelectionBehavior*` = Stop to trap focus in modals.
  - A custom `SelectionImageObject` replaces the default blue box.
  - B/back always closes.
  - Show input glyphs for the active device (UserInputService.PreferredInput / GamepadEnabled).
- **PC:** hover states, keyboard shortcuts shown on buttons, scroll-wheel support in lists.
- **VR:** avoid screen-edge HUDs. Use SurfaceGuis in world space.
- **Always test** in Studio's Device emulator: small phone, large phone, tablet, 1080p, 1440p, 4K, console.

## 7. Performance and memory (optimize)

- **Split ScreenGuis by update rate.** Any change re-renders its whole ScreenGui (LayerCollector), so ammo, timers and
  compass get their own ScreenGui, away from static frames.
- **Fewer instances:** flatten decorative nesting and reuse templates. Pool list rows, damage numbers and particles
  instead of creating and destroying them.
- **Avoid:**
  - TextScaled (~10× layout cost).
  - Tweening Size inside layouts.
  - Permanent CanvasGroups: each one is a texture, and it renders blank past the memory cap.
  - Over ~300 strokes or ~100 shadows on screen.
  - Per-frame work on hidden UI.
- **Texture memory:** atlas icons, keep images at the size they display (@2x at most), reuse 9-slice panels, and unload
  big screens' images when closed (Destroy or clear Image).
- **Profile** with MicroProfiler (`GuiLayerCollector::render2dContext`) and the Developer Console memory tab (GraphicsTexture,
  Gui).

## 8. Refinement commands

- **bolder:** raise one flat section to the strength the rest of the system already has. Bring in its display type,
  signature motif and accent at full strength. Don't add new colours or fonts. One decisive move, with everything around
  it quieted.
- **quieter:**
  - Desaturate to 70–85%.
  - Fewer colours.
  - Lighter weights.
  - Remove decorative strokes, gradients, glows and shadows.
  - Less motion.
  - Keep the point of view.
- **distill:**
  - Remove anything the player doesn't need for the task.
  - Collapse secondary info into on-demand panels.
  - Keep ≤ 4 choices per decision point.
- **clarify:** controls name their action ("Extract", "Equip"), errors name the problem and the fix, and terminology
  stays consistent across screens.
- **delight:** one memorable, on-brand moment (a stencil wipe, a satisfying loot tick-up), never gimmicks.

## 9. Copy, strokes, depth and texture (the anti-flat rules)

Added 2026-09-29 after user feedback on the shop screens: "alot of spam subtext… alot of 1 px strokes… the ui's seem to
look very flat". Each rule below is a hard floor.

### 9.1 Subtext budget (players don't read)

- **The default is no subtext.** A card is title + value/visual + action. Say things with the element itself: a badge
  ("ONE TIME"), a number ("+25%", "2X"), a timer, an icon, or colour/rarity. Icons with short labels beat sentences.
- **Budget:** at most **one** helper line per screen, and only if it changes a decision (for example "Odds shown before
  opening"). Put the rest in a tooltip, a long-press, an "i" button or a details panel.
- **Never write:**
  - Taglines under titles ("Everything you need to go PRO!").
  - Descriptions that restate the title ("Double coins forever" under 2X COINS).
  - Nudges ("Come back tomorrow for…").
  - Stacked marketing lines ("Best first purchase…" plus "Worth 3,100").
  - Muted footnote disclaimers.
  - Explanations of how the screen works.
- **Muted/dim text is never where information lives.** If the player needs it, show it at full contrast in a proper role.
  If they don't, delete it.
- **Test:** hide every secondary or muted line. If the screen still works, delete those lines. If it breaks, promote the
  one line that mattered into a badge, number or label.

**Plain words, fewest elements**: this applies to the immersive and competitive registers (SKILL.md Rule 3). User,
2026-09-29, on loading v2: "too much clutter and jargon". They then added: "it depends on the ui type… a roblox cash
grab needs alot of saturated textures and like appealing icons and animations". Info-dense screens may carry in-world
stat and lore vocabulary, and casual screens may be busy, but every register bans internal system names:
- Never surface internal system names such as loader stages (WORLD/PROFILE/ASSETS), "intel", "briefing", "signal
  acquisition" or classification tags. Players get plain words: the map name, a percent, one tip.
- Start every screen from the minimum set that does the job, then add only what the player would miss. A loading screen
  is the logo, the map name, one progress bar with a %, and one tip. Threat lists, conditions and stage breakdowns
  belong in the lobby or the map screen, if anywhere.
- Align the pieces to each other: the progress bar matches the title's ink width, and the icon and tip share a cap
  centre.

### 9.2 No hairlines (no 1-px strokes)

- **Why:** the design is drawn at 1920×1080 and one UIScale shrinks it to about 0.4–0.5× on phones. A 1-px stroke then
  renders sub-pixel, where it shimmers, disappears or looks like a web wireframe. Rows of thin outlined boxes are also a
  top "flat/template" tell.
- **Floor:**
  - No stroke under 2 px at the 1080p reference.
  - Functional strokes (selected, focus, rarity frame) are 2–4 px.
  - Stylistic outlines (cartoon ink) are 4–7 px and deliberate.
  - Otherwise use none.
- **Separate with light and tone instead of lines:**
  - A panel differs from what's behind it by about 6–12% lightness.
  - Use spacing and shadows.
  - For a divider, use spacing or an engraved groove: a 2-px dark line with a 2-px light line under it.
  - Use a border only for state (selected/focus), rarity, or an intentional thick outline style.
- **Roblox:**
  - Keep UIStroke on `FixedSize` under the single UIScale. `ScaledSize` has a usable range of only about 0–0.1 and
    reported UIScale bugs.
  - Keep ≤ 300 UIStrokes on screen.
  - The render order of strokes with the same ZIndex is undefined.
  - UIStroke doesn't affect layout, so leave room for it.

### 9.3 Depth: every surface answers "where is the light?"

Use one light from the top (slightly left). Build every large panel, card or button as a stack, from bottom to top:
1. **Shadow:** UIShadow (soft) for realistic styles, or a hard offset shadow for cartoon ones. Raised things cast more.
2. **Base fill with a value gradient:** the top is 4–10% lighter than the bottom. A large single-colour flat fill is
   banned.
3. **Material texture** from the game's world at 8–25%: painted steel, brushed metal, canvas, paper, rubber, plastic
   studs or carbon.
4. **Macro variation:** a large soft cloud noise or a vignette (darker toward the bottom and edges) so no area is uniform.
5. **Edge light:**
   - A 2–3 px top/left bevel highlight and a bottom/right shade, or an inner shadow.
   - Glossy styles get a top sheen.
6. **Wear** (gritty worlds only): edge wear, scratches and dust at 5–15%, concentrated on edges and corners, never
   uniform.
7. **Content**, plus a focal glow or rim light behind the hero object.

**Depth tiers**, from back to front, rise in contrast, saturation and shadow:
- the world behind the UI (darken or blur it behind modals);
- panels;
- raised cards;
- buttons and the hero.

**Buttons** get an extrusion (lip), a face gradient and a shine. The pressed state drops the lip and moves down.

**Items in shop hero slots and cards should be rendered objects**, not flat glyphs: render the item in Blender with a
three-point/rim light, or use the game's store renders, at @2x.

**Gradients that look good, and subtle texture** (user feedback on the item cards, 2026-09-29: "bad texture… needs
more of a subtle texture… make the color more poppy like arc raiders but make sure gradient look better"):
- **Interpolate gradients in OKLab**, never plain RGB (RGB blends go muddy and grey in the middle).
- Use 3–4 stops: a dark top of the **same hue** (L about 0.20, a little chroma), staying dark through the art area
  (16% at 0.45), then rising (50% at 0.75) to the full rarity colour at the bottom (L ≤ 0.6, chroma ×1.05).
- Add a soft radial bloom of the rarity colour behind the item's feet, plus a lighter radial spotlight (rarity mixed
  25% toward white) behind the item.
- Figma can't blend in OKLab. Compute the stops in code (Ottosson's OKLab matrices) and write them as explicit sRGB
  stops. In Roblox, a UIGradient with the same ColorSequence keypoints.
- Anything drawn on top of the bright bottom (tier bars, counts) needs its own contrast: a light tint of the rarity
  colour with a 1 px dark drop, on dark "empty" segments at 40% black.
- **Subtle material texture:** fine grain plus faint horizontal brushing. Use tileable Gaussian noise (a 3×3 wrap-blur
  mix) plus row noise stretched along x, baked white/black on transparency at a maximum alpha of about 110/255 and used
  at 50–55%. Scratches and grunge are for big panels in gritty screens, never on small item cards.
- **No decorative accent strokes** on corners or edges. The user rejected a lit rarity line on the cut corner.

### 9.4 Where production textures come from

- **Free (CC0, no attribution, commercial OK):**
  - [ambientCG](https://ambientcg.com/): 2,000+ PBR sets. Use the Color, AO or Roughness maps as UI grunge and material
    layers.
  - [Poly Haven textures](https://polyhaven.com/textures).
  - [ShareTextures](https://www.sharetextures.com/tag/free-cc0-texture), [TextureCan](https://www.texturecan.com/),
    [3dtextures.me](https://3dtextures.me/), [cc0-textures.com](https://cc0-textures.com/),
    [3DTexel](https://3dtexel.com/free-cc0-textures-3d-assets-the-3dtexel-library/).
- **Paid/pro (check the licence per item):**
  - [Envato Elements](https://elements.envato.com/graphics/game+ui): noise/grunge overlay packs and game UI kits.
  - [Fab](https://www.fab.com/category/material?lang=en): materials and UI packs.
  - [LayerLab GUI Pro kits](https://layerlab.io/collections/interface), the casual/RPG production reference for chunky
    buttons, frames and bevels.
  - [Unity Asset Store 2D GUI](https://assetstore.unity.com/2d/gui).
  - [Vecteezy topographic](https://www.vecteezy.com/free-vector/topographic-texture) and Adobe Stock for contour
    vectors.
- **Reference, not assets:** [Game UI Database](https://www.gameuidatabase.com/) and ArtStation/Behance UI breakdowns.
- **Licence rule:** log each texture's source URL and licence in `assets.json`. Prefer CC0. Never use unclear-licence or
  scraped images.

### 9.5 Make our own: 3D contour/relief and bevel textures (Blender pipeline)

- **Contour relief** (topographic lines with real depth):
  1. Make a plane with a noise heightmap and a Displace modifier.
  2. Add a shader contour-line mask by taking the height modulo an interval, as in
     [the Blender shader contour-map method](https://blog.edwardloveall.com/blender-shader-contour-maps).
  3. Render it orthographic from the top with a low-angle sun, as in
     [shaded relief in Blender](https://somethingaboutmaps.wordpress.com/2017/11/16/creating-shaded-relief-in-blender/).
  4. Export a grayscale seamless tile at 512–1024 px.

  Or trace it in Python (matplotlib contour plus PIL emboss) for flat line versions.
- **Bevelled panels and buttons:** model the frame with real bevels in Blender, light it with the UI light (top-left
  key, soft fill, rim), render orthographic, then 9-slice it. Real AO and bevel beat fake strokes.
- **Stud and plastic tiles:** generate them procedurally with PIL (see the stud recipe below).

### 9.6 Textures in Roblox (it only has alpha blending)

- Roblox has **no Multiply/Overlay blend modes**. Bake each texture as **white highlights plus black shades on
  transparency** (a neutral-grey area becomes fully transparent). Alpha-blended over any fill, it then behaves like
  Overlay, and one texture works on every colour. Never rely on Figma blend modes. If a layer needs one, bake the result
  to an `_img`.
- **Structure:**
  - The texture is an ImageLabel child above the fill and below the content.
  - Use `ScaleType.Tile` plus a pixel `TileSize` for materials, and `ScaleType.Slice` plus `SliceCenter` for bevel
    frames.
  - Set its strength with `ImageTransparency` and tint grayscale textures with `ImageColor3`.
  - Add a UIGradient on it to fade the texture toward the top or bottom.
- **Rounded corners:** ClipsDescendants clips rectangles only, so give the texture ImageLabel its own UICorner with the
  same radius.
- **Budget:** tiles 128–512 px, full panels ≤ 1024². Reuse the same few asset ids across screens (texture memory), and
  atlas small parts.

### 9.7 Shape language: never a screen of plain boxes

User feedback (2026-09-29): "alot of using just 1 shape, like the entire ui was just square". What credible sources say:
- **Riot, the League client "Visual Language of Hextech":** the whole UI is built from **three core shapes with
  jobs**:
  - the square is **structure** (stability, containers);
  - the diamond is **progression/accent** (it guides the eye);
  - the circle is **focus** (it draws attention to the primary item).

  Their combination frames the key areas of attention.
- **Google Material 3 (46 studies, 18k+ participants):**
  - Shape directs attention, identifies components, communicates state and expresses brand.
  - Contrasting shapes create tension, which makes a design memorable, and expressive shape, size and containment let
    users find key elements up to 4× faster.
  - But **don't break familiar patterns or drop labels**, which hurt usability in their tests.
  - Nested shapes need **optical roundness**: the inner radius is the outer radius minus the padding, never the same
    radius.
  - Corners come in families: rounded and **cut** (chamfered), symmetric or asymmetric.

**Rules:**
1. **Define 3 shapes per game, each with a job,** before drawing:
   - **structure:** most containers, about 70% of the area;
   - **accent/direction:** 1–3 elements per screen, such as the CTA, active tab, section markers or progress;
   - **focus:** the single focal thing, such as the hero item, timer ring, avatar or objective.
2. **Examples:**
   - Dead Signal (industrial extraction): structure = rectangles with **cut/chamfered corners** (one or two corners,
     asymmetric); accent = parallelograms and chevrons (skewed tabs, hazard stripes, arrows); focus = circles and rings
     (radial timers, item focus rings).
   - Stud/simulator: structure = soft rounded rectangles; accent = starbursts, ribbons and tilted tags; focus = circles
     and blobs.
3. **Break the box silhouette on purpose:**
   - the hero art overlaps its container edge;
   - tabs and notches attach to panels;
   - labels sit on a tab cut into the frame edge;
   - use one asymmetric corner;
   - a ribbon crosses an edge;
   - vary the aspect ratios (one tall hero, not a grid of equal cards).
4. **Contrast = attention:** the one element that must be found (the buy button, claim button or objective) uses the
   accent or focus shape. Everything else stays structural. Don't give everything a special shape, or nothing stands
   out.
5. **Roblox build:**
   - UICorner rounds only (per-corner radii work).
   - Cut corners, parallelograms, chevrons and diamonds come from **9-slice images baked from the Figma vector at
     @2x** (keep the cut inside the fixed slice corners). You can also use a rotated Frame for small diamonds, but
     rotated frames don't clip children.
   - Path2D draws lines and curves (strokes), not filled polygons.

### 9.8 Tips, hints and "floating" boxes

User feedback (2026-09-29) on the loading screen's "FIELD TIP 03/12" card: it was a floating tip box that wasn't
thought through, with buzz text.
- **Why generic tips fail:**
  - NN/g: tips pushed out of context interrupt the user's goal, aren't remembered and don't improve task performance.
    Contextual **pull** help at the moment of need works: a tooltip, coach mark or step hint, easy to dismiss and
    easy to find again.
  - Celia Hodent (Fortnite UX, GDC "The Gamer's Brain"): players don't see info that competes for attention, so
    **teach at the moment of the action**, through the thing itself.
- **Do this instead:**
  1. Teach in context. For example, while bandaging, the progress ring shows move-cancel glyphs ("Sprint, roll or jump
     cancels") right there, and a first-time hint appears when the player first sprints mid-heal.
  2. Keep a **field manual/codex** menu where every tip can be read again. The Xbox Accessibility Guidelines say to make
     loading-screen info accessible later and give players time to read.
  3. Keep a loading-screen tip only if it is **built into the composition**:
     - one line, ≤ 12 words, action first;
     - paired with a visual (the item icon or key/button glyphs);
     - anchored to the layout (e.g. above the progress bar, aligned to the grid), not a box floating in space;
     - no eyebrow label or counter ("FIELD TIP 03/12" is buzz text);
     - full contrast;
     - shown long enough, with a button to cycle;
     - picked for the current map, mode or loadout, not at random.
- **Nothing floats:** every element anchors to a screen edge, a grid column or the object it describes (a callout gets a
  leader line or pointer to its subject). A lone box in empty space is a bug.

### 9.9 Size and position are computed, then measured (never eyeballed)

User feedback (2026-09-29) on a price pill: the text size and position weren't reasoned out, the Robux icon wasn't
centred and the numbers weren't aligned. The cause: display fonts (Luckiest Guy, Oswald, etc.) have line boxes that
aren't centred on their glyphs, so centring the text **box**, or an auto-layout row, puts the digits off-centre. The
fix is a sizing system plus measurement.

**Sizing system (derive every number, write the derivation down):**
- **Button label cap height = a share of the visible face** (the face inside the stroke and above the lip):
  - price pill 0.54;
  - primary CTA 0.50;
  - small square (+) 0.50;
  - tab/secondary 0.40.

  Font size = capHeight ÷ the font's cap ratio. Measure the ratio from the ink of "H0" at a known size, never guess it.
- **Siblings share one size.** Every price pill, tab or CTA of the same height uses the same font size. Derive it from
  the font's cap ratio, **not** from each string's ink ("399" and "149" have different ink but must match).
- **Padding floor:** at least 1 cap height of clear space on each side of the label group. If a sibling fails, lower the
  group's size or widen the buttons. Never let one label touch its edges.
- **Icon beside a number or label:** icon height = 1.3–1.5 × cap height, gap = 0.3 × cap height. The icon's centre sits
  on the **cap band's centre**, and the whole group (icon + gap + text ink) is centred on the face.
- **Stacked content** (icon, name, button in a tile): pin the button to the bottom padding, then centre the name's
  **ink** in the gap between the icon and the button. The gaps above and below the name must match to ±2 px.
- **Alignment:** repeated elements line up on shared edges or centres. Items in a row bottom-align with the CTA next to
  them, and titles centre in the space they own.

**Measure (in Figma, with use_figma):**
```js
// First: await figma.loadFontAsync(t.fontName) for every font used (ink() rewrites characters).
// Ink bounds relative to the text's x/y: strip stroke and effects on a clone, read absoluteRenderBounds.
function ink(t,str){const c=t.clone();figma.currentPage.appendChild(c);c.strokes=[];c.effects=[];if(str)c.characters=str;
  c.x=0;c.y=-5000;const b=c.absoluteRenderBounds;const r={l:b.x-c.x,t:b.y-c.y,w:b.width,h:b.height};c.remove();return r;}
// Centre the cap band vertically and the ink horizontally at (cx, cy):
// k=ink(t); kc=ink(t,'H0'); t.x=cx-k.w/2-k.l; t.y=cy-kc.h/2-kc.t
```
- Take labels out of auto layout (`layoutMode='NONE'`) when you place them by ink. Auto layout centres boxes, not
  glyphs.
- **Report the numbers** after every layout pass. For each button: font size, ink centre vs face centre, and icon centre
  vs ink centre (must be within 1 px). For each stack: the gaps. Fix anything off before taking the screenshot.
- In Roblox: set `TextYAlignment=Center`, then apply a per-font vertical nudge measured once from the same ink test (a
  UIPadding top/bottom offset on the label). Record the nudge per font in the theme tokens.

### 9.10 Fix reference: measured corrections the user asked for (apply by default)

From the Seed Shop review (2026-09-29): "the X in the close button isnt centered, the name of the seed and the rarity is
too close, the color of the numbers isnt contrasted".

1. **Icon-only buttons (close X, +, arrows):** centre the glyph's **rendered bounds** (`absoluteRenderBounds` of the
   top/white icon layer) on the **visible face**: x = width/2, y = (stroke + faceHeight)/2, where the face sits above the
   lip. Don't centre the icon frame or the whole button. The lip and the sticker's drop copy both push the frame centre
   off. The measured offset must be 0 ±1 px.
2. **Stacked text (name over tag or meta line):** measure from the name's **lowest ink**, meaning descenders (use the
   string "Hgjpqy") plus the text outline, down to the next element's top.
   - Minimum gap 8 px at 1080p (≈ 0.35 × cap height) below the descender and outline. That's about 20 px from the
     baseline when a name has no descenders.
   - Then centre the whole group (name outline top to meta bottom) in the row, ±1 px, with equal top and bottom padding.
   - Never space by cap height alone.
3. **Numbers must be the highest-contrast text in their container.** On saturated mid-light faces (yellow, orange,
   lime, cyan), white text alone is about 1.4:1 and dark ink alone reads muddy against the loud chrome.
   - Use the screen's display-text system: a white fill, a ≥ 4–5 px dark ink outline (outline vs fill ≈ 17:1) and a
     hard ink shadow of about 3 px. Every price, count and timer uses the same treatment.
   - Check contrast numerically (WCAG luminance) for fill vs outline and outline vs face.
4. **Adding an outline changes spacing:** an icon-to-text gap must be `0.32 × cap + outlineWidth`. Centre the **visual**
   group (icon left edge to the text outline's right edge), not the unoutlined ink.

After any fix, re-run review.md's alignment check and report the numbers (offsets, gaps, contrast) before the
screenshot.

### 9.11 Colour roles and the selected state (approved 2026-09-29)

The review board is in Figma: "Colour & Selection Reference" on the Stud Store page. The user picked **bright fill**:
"the bright fill looks the best, u could also make it so the sizing on the highlighted one is bigger, and the others
move up, using like a ui layout".

**Why the first highlight failed:** a yellow ring on light green measured 1.4–1.7:1, below the 3:1 minimum, and colour
was its only cue. A light hue on a light surface disappears. **Selection must change lightness**, not just hue.

**Colour rules** (Impeccable colorize/operate/craft-floor, Xbox XAG 102/113, WCAG 2.2, Roblox Creator docs, Roblox staff
DevForum guide):
1. **Colours are roles.** Pick the roles before swatches: chrome, reading surface, action (buy), reward (claim),
   danger (close), selected, disabled and ink. Each role has one job and means the same thing on every screen.
2. **Selection = a lightness jump + at least 2 cues.** The selected item changes lightness by ≥ 3:1 against its
   neighbours and adds a ring, a lift/shadow, a size change or a pointer. XAG 113 examples: The Outer Worlds (outline +
   contrasting block fill + text change) and Fallout 76 (yellow backdrop + pointer character).
3. **The accent is only for action and selection.** Buy and claim colours never decorate, and inactive items stay
   quieter.
4. **Vivid = important, muted = less important** (Roblox docs). The most saturated hue goes on the thing to press.
5. **Never colour alone.** Rarity, sold-out and danger states always also carry a label, icon or shape.
6. **Contrast is measured, not eyeballed** (WCAG luminance). Body text ≥ 4.5:1. Large text, icons and focus ≥ 3:1
   against what's actually behind them. An ink outline counts: white + ink is about 17:1.
7. **Solid over see-through.** Use explicit colours rather than stacked transparency, and respect `PreferredTransparency`.
8. **Tint, don't grey.** Secondary text on a coloured surface is a shade of that hue.

**The approved selected-row pattern (casual register):**
- **Fill:** a bright cream-yellow gradient, #FFF6C8 → #FFE27A (≈ 3.8:1 lighter than the #2A8A36 rows), with a 5 px ink
  ring and a hard ink drop of 6 px. Studs drop to 30%.
- **Text:** the name keeps white + ink outline. Small text on the cream (the stock count) switches to plain ink.
- **Size:** the selected row **grows** (100 → 120 px tall, plate 76 → 88, icon 56 → 66, name 34 → 38). The rows live in
  a vertical list layout, so the others move automatically (Figma auto layout, UIListLayout in Roblox).
- **Gamepad:** use the same bright-fill treatment for `SelectionImageObject` / `GuiService.SelectedObject`, so gamepad
  focus looks identical to the mouse selection.

**Reference casual role palette** (Seed Shop):
- chrome #6BDB55;
- reading row #2A8A36;
- buy #FFD84D;
- claim #FF46B5;
- danger #FF4D5E;
- selected #FFF1A8;
- disabled #C3CAD4;
- ink #1E1A10.

The rarity ramp steps both hue and lightness (Common #C9D1DC, Uncommon #7BE86B, Rare #4DA6FF, Epic #B36BFF, Legendary
#FFC928, Mythic #FF5EC4), always with the name on a pill.

## Sources

- **Roblox:**
  - [Cross-platform design](https://create.roblox.com/docs/ui/cross-platform-design)
  - [UI/UX design](https://create.roblox.com/docs/production/game-design/ui-ux-design)
  - [Designing UI tips](https://devforum.roblox.com/t/designing-ui-tips-and-best-practices/3074034)
  - [Size modifiers](https://create.roblox.com/docs/ui/size-modifiers)
  - [ScreenGui](https://create.roblox.com/docs/reference/engine/classes/ScreenGui)
  - [Top bar inset](https://devforum.roblox.com/t/what-are-the-new-topbar-inset-dimensions/3237388)
  - [Flex layout](https://devforum.roblox.com/t/flex-features-for-uilistlayout-client-release/3096190)
  - [UIStroke release](https://devforum.roblox.com/t/full-release-uistroke-improvements-scaling-offsets-and-more/3958036)
  - [UIShadow and corners](https://devforum.roblox.com/t/full-release-new-ui-capabilities-shadows-individual-corners/4636263)
  - [Gradients beta](https://devforum.roblox.com/t/studio-beta-upgraded-ui-gradients/4846594)
  - [Styling](https://devforum.roblox.com/t/full-release-ui-styling-is-officially-released/4275082)
  - [StyleQuery](https://devforum.roblox.com/t/full-release-stylequery-more-styling-features/4566519)
  - [9-slice](https://create.roblox.com/docs/ui/9-slice)
  - [Builder font](https://devforum.roblox.com/t/introducing-builder-font-deprecating-gotham-and-arial/2868222)
  - [Font enum](https://create.roblox.com/docs/reference/engine/enums/Font)
  - [Rich text](https://create.roblox.com/docs/ui/rich-text)
  - [Gamepad selection](https://devforum.roblox.com/t/new-gamepad-ui-selection-apis/1791278)
  - [Static UI performance](https://devforum.roblox.com/t/static-ui-performance-improvements/222557)
  - [Roadmap fall 2026](https://devforum.roblox.com/t/creator-roadmap-2026-fall-update/4880208)
- **Game UI:**
  - [ARC Raiders UX](https://uxingames.com/2025/12/27/arc-raiders/)
  - [Hunt HUD](https://huntshowdown.wiki.gg/wiki/HUD)
  - [HUD design](https://nastyrodent.com/what-is-hud-in-games/)
  - [Diegetic UI types](https://www.gamedeveloper.com/design/game-ui-discoveries-what-players-want)
  - [UI and story/brand](https://vsquad.art/blog/expert-interviews/game-ui-ux-story-brand/)
  - [AI design slop](https://www.developersdigest.tech/blog/ai-design-slop-and-how-to-spot-it)
  - [Xbox text size](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/101)
  - [Target size](https://tetralogical.com/blog/2022/12/20/foundations-target-size/)
  - [Game UI Database](https://www.gameuidatabase.com/)
- **Copy, strokes, depth, textures (§9):**
  - [Icons vs text](https://blog.thenounproject.com/how-to-use-icons-in-ui-and-ux-design-best-practices/)
  - [Icon usability, NN/g](https://www.nngroup.com/articles/icon-usability/)
  - [Mobile game UI best practices](https://www.linkedin.com/pulse/mobile-game-uiux-top-10-best-practices-troy-dunniway)
  - [Fewer borders, more shadow and space](https://www.adhamdannaway.com/blog/ui-design/ui-design-tips)
  - [Containers and borders](https://designerup.co/blog/ui-design-tips-boxes-and-borders/)
  - [UIStroke UIScale bug](https://devforum.roblox.com/t/uiscale-incorrectly-scaling-uistroke-thickness/4157250)
  - [ScaledSize range](https://devforum.roblox.com/t/uistroke-scaledsize-thickness-slider-uses-wrong-number-range/4327390)
  - [Bevel via two inner shadows](https://sarunw.com/posts/how-to-make-bevel-effect-in-swiftui/)
  - [Shadows and blurs](https://hype4.academy/articles/design/ui-design-shapes-objects-basics-shadows-and-blurs)
  - [Material layering](https://generalistprogrammer.com/tutorials/substance-painter-game-texturing-complete-pbr-workflow)
  - [Free texture sites 2026](https://app.cinevva.com/guides/free-textures-hdris-materials)
- **Colour and selection (§9.11):**
  - [Impeccable colorize](https://github.com/pbakaus/impeccable/blob/main/skill/reference/colorize.md)
  - [XAG 113 focus](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/113)
  - [XAG 102 contrast](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102)
  - [Roblox: choose an art style](https://github.com/Roblox/creator-docs/blob/main/content/en-us/tutorials/curriculums/user-interface-design/choose-an-art-style.md)
  - [Roblox accessibility](https://create.roblox.com/docs/production/publishing/accessibility)
  - [Roblox staff: Designing UI tips](https://devforum.roblox.com/t/designing-ui-tips-and-best-practices/3074034)
  - [Gamepad UI highlight](https://devforum.roblox.com/t/updated-gamepad-ui-highlight-improvements/1582185)
  - [M3 states](https://m3.material.io/foundations/interaction/states/applying-states)
- **Shape language and tips (§9.7–9.8; credible sources only):**
  - [Riot: Hextech client UI](https://www.riotgames.com/en/news/under-hood-league-client%E2%80%99s-hextech-ui) and the
    Visual Language of Hextech (square = structure, diamond = accent, circle = focus)
  - [Material 3 shape](https://m3.material.io/styles/shape/overview-principles) and
    [corner scale](https://m3.material.io/styles/shape/corner-radius-scale)
  - [Google: expressive design research](https://design.google/library/expressive-material-design-google-research)
  - [Building with M3 Expressive](https://m3.material.io/blog/building-with-m3-expressive)
  - [Bungie, David Candland: Interface of Destiny (GDC)](https://gdcvault.com/play/1023460/Tenacious-Design-and-The-Interface)
  - [NN/g: onboarding tutorials vs contextual help](https://www.nngroup.com/articles/onboarding-tutorials/)
  - [Celia Hodent: Gamer's Brain, onboarding (GDC16)](https://celiahodent.com/gamers-brain-ux-onboarding/)
  - [Hodent UX lesson](https://www.gamedeveloper.com/design/a-quick-ux-lesson-from-gdc-masterclass-teacher-celia-hodent)
  - [Xbox Accessibility Guideline 101 (text/loading tips)](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/101)
  - [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/full-list/)
  - Source rule: take design rules only from shipped-studio designers (GDC, studio blogs), platform guidelines
    (Material, Apple HIG, Xbox XAG, Roblox docs) and established UX research (NN/g, Hodent). Anonymous blogs are at most
    leads to verify.

## Saturated "stud" simulator style (the casual register recipe; first pass 2026-09-29)

For bright simulator or shop UI ("very saturated stud UI"), the brief overrides the restraint defaults. §9 still applies:
no tagline or description subtext, and depth on every surface. Build it like this:
- **Ink outline on everything:** one dark ink colour (#1B0F3B). Panels get a 6-px inside stroke, buttons 5 px, and text
  an outside stroke of about fontSize/11 plus a hard drop shadow (radius 0, y about fontSize/14). In Roblox that is
  UIStroke (Outer) plus an offset label copy.
- **Plastic studs:** Roblox's **square** stud tile (see "Roblox stud UI" below; never round studs) in TILE mode at
  25–55% over saturated panels and the background.
- **Chunky buttons:** a lip colour for the body; a face 86% tall with a gradient from face+30% white down to the face; a
  white shine pill at 38%; and a hard ink shadow at y 6. Green means buy, pink means claim, yellow means the active tab,
  blue means an inactive tab, and a white pill with ink text is the price on a coloured tile.
- **Sticker icons:** Lucide SVG built three times: an ink copy offset down, an ink copy with a thick stroke as the
  outline, and a copy with a white stroke and a colour fill on top. Replace Lucide glyphs that read badly when filled:
  coins → a custom round coin (two circles plus a bar), clover → four circles plus a stem.
- **Energy:** vertical two-stop gradients per card (pink→orange, cyan→blue, lime→green), sunburst rays at 17% white
  behind hero art, a radial white glow behind icons, 14-point starburst badges tilted ±10–12°, and tilted tag ribbons.
- **Fonts:** Luckiest Guy for display, numbers and buttons, and Fredoka One for body text (both ship in Roblox).

### Roblox stud UI (the Grow a Garden-era look): SQUARE studs, not round

User correction (2026-09-29): "why are u using the circular stud, use this kind of stud". The stud UI every big
simulator uses is Roblox's **square** stud: bevelled rounded squares with a lighter top, a bright top/right edge, a dark
left/bottom edge and a soft drop. Never use round/LEGO-style studs for this.
- **Source (exact):** Roblox's own surface sheet at `%LOCALAPPDATA%/Roblox/Versions/<studio>/PlatformContent/pc/textures/studs.dds`.
  It's 128×2048 with 16 cells of 128 px:
  - cells 0–3: raised studs, 2×2 per cell;
  - cells 4–7: weld/glue X marks;
  - cells 8–11: inlets;
  - cells 12–15: mixed/universal.

  Take **cell 0**. PIL opens DDS directly.
- **Convert to an overlay:** neutral grey is 128, which becomes transparent.
  - `d = clip((L − 128) / 72.7 × 1.3, −1, 1)`.
  - **Lift the stud tops:** set `d = 0.38` wherever L ≈ 136 (the flat stud face), so the studs read as lighter raised
    squares like the reference. Without the lift they read as hollow outlines at UI scale.
  - Write RGB 255 where d > 0 and 0 where d < 0, with alpha |d|.
  - The file is square_stud_128.png (Figma hash f0a15729…).
- **Scale:** TILE scalingFactor about 0.6 (about 38 px stud pitch at 1080p).
  - Opacity 50–55% on chrome (header, window, background).
  - At most 15% under reading rows.
  - About 35% on small icon plates.
- **In Roblox:** an ImageLabel with `ScaleType.Tile`, `TileSize` = UDim2.fromOffset(77, 77) for the 128-px/2×2 tile,
  `ImageTransparency` about 0.45, and the colour from the panel's BackgroundColor3/UIGradient underneath. Upload the
  PNG; the DDS can't be used in an ImageLabel.
- **Corners:** stud shops read best with **tight corners** (radius 6–12 px: window 12, panels 10, rows, buttons and plates 8,
  pills 6). The user asked for "less rounded corners" (2026-09-29). Keep the one focus shape (a circle plate) round.
- **Icons:** use the Roblox vector icon packs ([icon-packs.md](icon-packs.md)), not Lucide.
- **Simple casual shop pattern:**
  - one-column rows: a rarity-coloured icon plate, the name, a rarity pill with "N LEFT", and one big price button;
  - a restock timer next to the title;
  - a red close button;
  - the wallet at the bottom-left.

  Sold out is a grey "SOLD OUT" button with no stock line.
