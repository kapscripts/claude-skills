# Motion: amazing Roblox UI animation

Motion should explain state, confirm actions, and give each screen one authored moment. Anything else is animation debt.
Great game UI motion is **fast, confident, layered with sound, and scaled to the event's importance**.

## 1. Find the job first

For each screen, write a four-line motion plan before touching tweens:
- **Focal moment:** the one sequence worth authoring. On a loot screen it's the rare-item reveal; on the HUD it's damage
  taken; on the inventory it's picking up an item.
- **Continuity:** which state or layout changes need explaining (a panel opens from its button; an item flies to its slot).
- **Feedback:** every control acknowledges input within 100 ms.
- **Budget:** what may be expensive (CanvasGroup fades, particles, ViewportFrame spins) and when it must stop.

A generic fade-and-rise on everything is not a plan.

## 2. Timing and easing tokens

Keep every screen on these (`UIMotion.T`):

| Use | Duration | Easing |
|---|---|---|
| Press feedback | 60–90 ms | Quad Out, down to 0.94–0.97 |
| Hover / focus | 100–150 ms | Quint Out, up to 1.03–1.05 |
| Release | 150–220 ms | **Back Out** (the one place overshoot belongs) |
| Panel / modal open | 220–300 ms | Quint Out: fade plus a 16–24 px slide, or 0.97→1 scale |
| Panel close | 140–200 ms | Quad In: exits are faster than entrances |
| List stagger | 25–40 ms per item, **capped at ~8 items** (≈ 300 ms total) | later items appear with no extra delay |
| Toast | 250 ms in, 3–4 s hold, 180 ms out | |
| Hitmarker | 40–60 ms in, 150–250 ms out | |
| Damage number | pop 1→1.2→1 in ~120 ms, drift and fade over 0.6–0.8 s | |
| Ghost health bar | hold 0.4–0.6 s (restarts on each hit), then drain 0.3–0.5 s | |
| Big reveal (rare loot) | 0.8–2 s total, **skippable** | |

- **Easing:**
  - Entrances decelerate (Quint/Exponential Out).
  - Exits accelerate (Quad In).
  - Continuous things are Linear: progress fills, spinners, shine sweeps.
  - Elastic and Bounce: essentially never.
- **Durations:**
  - 100–400 ms covers almost all UI.
  - Over ~500 ms for a routine action feels like lag.

## 3. The principles that make it feel expensive

- **Anticipation:** a tiny dip or charge before a big payoff (reward chest shakes 0.4 s before it opens).
- **Staging:** one thing moves at a time where attention matters. Don't animate the whole screen at once.
- **Follow-through and overlap:** children settle 30–60 ms after their parent (the icon lands after the card).
- **Squash and stretch:** only in playful styles, on press (X 1.06, Y 0.94). An extraction shooter stays crisp and
  mechanical.
- **Scale to importance:**
  - Common pickup: a 150 ms slide-in and a click.
  - Legendary: anticipation, then a 60 ms white flash, a Back Out scale 0.6→1, a rotating rarity-coloured gradient behind
    the card, a UIStroke pulse, a shine sweep, a number count-up, and a heavier sound.
  - Every tier must feel different.
- **Juice is layered:** tween + **sound** (real recorded, matched to the motion) + particles (pooled ImageLabels) + camera
  or screen shake where it fits (1–3 px small, 5–10 px big) + hit-stop for impact. Motion without sound feels dead.
- **World-fitting motion:**
  - A rugged extraction shooter uses mechanical, snappy motion: slides, shutter wipes, scan lines, stencil flickers.
  - A cosy game uses soft springs.
  - Pick the motion vocabulary from the fiction, the same way as colour and type.

## 4. What looks cheap or AI-made

(For the immersive/competitive registers. The casual register deliberately uses more motion; see §4b.)

- Elastic or Bounce everywhere, overshoot on exits.
- Every element fading in at once with the same timing.
- 0.5–1 s routine animations, Linear movement, uncapped staggers.
- Static UI that bobs or pulses forever.
- Hover that snaps back or jitters when the mouse leaves mid-tween, because it isn't interruptible.
- Animating TextSize, Size inside layouts, or UIStroke thickness on text (it flickers).
- The same animation for every rarity or importance level.
- No sound.

## 4b. Casual/simulator register: motion that sells (SKILL.md Rule 3)

A simulator or monetized shop should feel alive. Motion goes **only on things that sell or celebrate** (offers, CTAs,
rewards, new items), never on static chrome. At most 2 idle-animated elements are visible at once, so they don't
compete. Respect `ReducedMotionEnabled`: swap idle loops for a static glow.

**Idle, on offers and CTAs:**
- **Pulse:** UIScale 1 → 1.06 → 1, 1.4–1.8 s, Sine InOut, looped. Use it on the primary buy/claim button or the hero
  badge.
- **Shine sweep:** UIGradient Offset −1 → 1 over 0.6 s (Quad Out), repeated every 3–4 s. Use it on the hero price
  button and premium tiles.
- **Badge wobble:** Rotation ±6° twice over 0.4 s, every 5 s. Use it on "HOT!", "BEST!" and "NEW" starbursts.
- **Rays:** sunburst rotation of 6–10 °/s behind hero art.

**Feedback:**
- **Hover:** UIScale 1.05 over 0.12 s (Back Out, mild).
- **Press:** 0.94 over 0.07 s, then release to 1.0 (Back Out). The face drops onto its lip.

**Rewards and purchases:**
- **Pop-in:** scale 0 → 1.15 → 1 over 0.35 s (Back Out).
- **Count-up:** 0.6–1.0 s.
- **Burst:** confetti or coin particles, 20–40 of them.
- **Sound:** a bright success sound.
- **Tile arrival:** new tiles arrive staggered 40 ms apart and slide up 12 px.


**Selected row grows in a list** (approved 2026-09-29):
- The rows sit in a UIListLayout (Padding 14).
- On select, tween the chosen row's `Size.Y.Offset` from 100 to 120 over 0.18 s (Quint Out). The layout moves the
  neighbours every frame, which is the approved "others move up" feel.
- Also tween an inner content UIScale from 1 to 1.06 in the same time. Swap the fill to bright cream within 0.1 s.
- Deselect runs the same tweens in reverse over 0.14 s (exits faster).
- This is the one sanctioned exception to "don't tween Size inside layouts". It's fine for short lists (≤ 12 rows). For
  long scrolling lists, animate only the inner UIScale and the fill.
- Honour ReducedMotion: snap the size and fill with no tween.

**Timers:**
- The last 60 s of a limited-time offer tick with a pulse.
- The text never shakes.

## 5. Roblox tools

- **TweenService:** the default. Styles: Linear, Sine, Quad, Cubic, Quart, Quint, Exponential, Circular, Back, Bounce,
  Elastic.
  - A newer tween on the same property cancels the older one. Still `:Cancel()` your own handle (UIMotion keeps one live
    tween per instance+channel) so stale Completed handlers don't fire.
  - `TweenService:GetValue(alpha, style, dir)` gives eased curves for custom loops (tickers, Path2D motion).
  - Cache TweenInfos. Never create tweens every frame.
- **Springs**, for hover, drag and anything retargeted constantly, because they keep velocity when interrupted:
  - **spr** (Fraktality): `spr.target(obj, damping, frequency, {props})`. Damping 1 is neutral, 0.6–0.8 gives pop. Handles
    UDim2 and Color3.
  - **Ripple** (`littensy/ripple`).
  - **Fusion 0.3** `Spring`, if the UI is Fusion.
  - **react-spring** for react-lua.
  - `TweenService:SmoothDamp(cur, target, vel, smoothTime, maxSpeed, dt)` is built in (number, Vector2, Vector3,
    CFrame; not UDim2).
- **Per-frame followers:** `RunService.PreRender` (RenderStepped is superseded). Always use `dt`:
  `x = target + (x - target) * 2^(-dt/halfLife)` (`UIMotion.damp`). A fixed `lerp(a, b, 0.1)` per frame depends on the
  frame rate. Clamp dt (`math.min(dt, 1/15)`) after hitches.
- **What to animate:**
  - **UIScale.Scale**, not Size, for pops. It scales text, strokes and children together without re-layout. Inside a
    UIListLayout, put the animated frame in a holder frame so it scales from its centre.
  - Position, Rotation and AnchorPoint (set 0.5, 0.5 before scaling or rotating).
  - Image, Text and Background transparency.
  - CanvasGroup `GroupTransparency` for whole-panel fades only. It costs a texture and renders blank past the memory cap,
    so keep it short-lived and fixed-size.
  - **UIGradient Offset and Rotation** for shine sweeps, cooldown radials (two half-circle masks with a hard-edged
    gradient) and loading bars. Animate Offset/Rotation, never rebuild the sequences.
  - UIStroke Color/Transparency for focus rings and rarity glows.
  - `TextLabel.MaxVisibleGraphemes` for typewriter text (layout is fixed, so there's no jitter).
  - `ImageRectOffset` stepping for sprite-sheet animation.
  - Path2D (`GetPositionOnCurveArcLength`) for curved fly-to-inventory paths.
  - ViewportFrame for 3D item previews: spin only while visible.
  - UIPageLayout: change its default Back 1 s tween to Quint Out ~0.3 s.
- **Styling Transitions (2026):** `StyleRule:SetPropertyTransitions({Prop = TweenInfo})`. The engine animates state
  changes natively, faster than Luau, and it's good for hover/press colour on many buttons.
- **Coming soon (Roblox roadmap):** native 2D particles, animated image containers, UI backdrop blur. Re-check the docs.

## 6. Engineering rules

- **Interruptible by design:**
  - Panels are state machines (Closed, Opening, Open, Closing; `UIMotion.panel`), so spamming a toggle reverses from the
    current state.
  - Springs retarget.
  - Tweens cancel the previous handle.
- **Cleanup:** every connection, PreRender binding and looping tween belongs to a Trove/Janitor/Maid (or the cleanup
  function UIMotion returns) and is destroyed with the UI.
- **Performance:**
  - Animate a few properties on a few objects.
  - Keep HUD animation in its own ScreenGui, away from static UI (any change re-renders the whole ScreenGui).
  - No TextScaled; it's ~10× the layout cost.
  - Pause loops when hidden.
- **Reduced motion:** when `GuiService.ReducedMotionEnabled` is on, replace slides, scales, shakes and spins with quick
  fades or instant state changes. Keep feedback that confirms an action. UIMotion does this automatically.
- **Gamepad:** `SelectionGained`/`SelectionLost` drive the same hover state as the mouse. Replace the default selection
  box with a custom `SelectionImageObject` (for example an animated UIStroke frame).

## 7. Recipes

All of these are in `scripts/UIMotion.lua`, tested:

```lua
local UIMotion = require(ReplicatedStorage.UIMotion)
local cleanup = UIMotion.fitDesignScale(screen.Root)          -- Figma-size root fitted to any screen
local unbind = UIMotion.button(screen.Root.Card.Take_btn)       -- hover 1.04 / press 0.95 / Back Out release, gamepad aware
local panel = UIMotion.panel(screen.Root.Card)                  -- panel:open() / :close() / :toggle()
local setHealth = UIMotion.ghostBar(hud.Health.Fill, hud.Health.Ghost)   -- setHealth(0.42)
UIMotion.countUp(label, 0, 1250, 0.6, "%d")                     -- number ticker
UIMotion.typewrite(dialogueLabel, 45)                           -- characters per second
UIMotion.shine(card.ShineOverlay)                               -- diagonal sweep
UIMotion.stagger(rows, function(row) UIMotion.panel(row):open() end)   -- capped stagger
```

**Legendary reveal (sketch):**

```lua
UIMotion.tween(card.MotionScale, TweenInfo.new(0.4, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, 3, true), {Scale = 1.02}) -- charge
task.wait(0.45); flash.BackgroundTransparency = 0
UIMotion.tween(flash, TweenInfo.new(0.06), {BackgroundTransparency = 1})
card.MotionScale.Scale = 0.6
UIMotion.tween(card.MotionScale, UIMotion.ease.pop(0.25), {Scale = 1})
UIMotion.tween(glow.UIGradient, TweenInfo.new(6, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), {Rotation = 360}) -- stop when closed
UIMotion.shine(card.ShineOverlay); UIMotion.countUp(card.Value, 0, item.value, 0.6)
-- + sound per beat; reveal skippable on any input
```

## Sources

- **Roblox:**
  - [UI animation](https://create.roblox.com/docs/ui/animation)
  - [TweenService](https://create.roblox.com/docs/reference/engine/classes/TweenService)
  - [SmoothDamp](https://create.roblox.com/docs/reference/engine/classes/TweenService#SmoothDamp)
  - [EasingStyle](https://create.roblox.com/docs/reference/engine/enums/EasingStyle)
  - [CanvasGroup](https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/CanvasGroup.yaml)
  - [Text best practices](https://devforum.roblox.com/t/all-about-text-best-practices/1515743)
  - [Styling transitions](https://devforum.roblox.com/t/full-release-styling-transitions/4646870)
  - [GuiService ReducedMotion](https://create.roblox.com/docs/reference/engine/classes/GuiService)
  - [Radial cooldowns](https://devforum.roblox.com/t/circularradial-progresscooldown/4320264)
- **Motion libraries:**
  - [spr](https://github.com/Fraktality/spr)
  - [Ripple](https://github.com/littensy/ripple)
  - [Fusion springs](https://elttob.uk/Fusion/0.3/tutorials/animation/springs/)
  - [react-spring (Roblox)](https://github.com/chriscerie/roact-spring)
- **Motion design:**
  - [NN/g animation duration](https://www.nngroup.com/articles/animation-duration/)
  - [Material duration/easing](https://m1.material.io/motion/duration-easing.html)
  - [Material 3 tokens](https://m3.material.io/styles/motion/easing-and-duration/tokens-specs)
  - [Disney principles in UI](https://ixdf.org/literature/article/ui-animation-how-to-apply-disney-s-12-principles-of-animation-to-ui-design)
  - [Juice it or lose it (GDC)](https://www.gdcvault.com/play/1016487/juice-it-or-lose)
  - [Frame-rate independent damping](https://www.rorydriscoll.com/2016/03/07/frame-rate-independent-damping-using-lerp/)
  - [Game UI Database](https://www.gameuidatabase.com/)
  - [Valorant UI motion](https://www.davidkim.design/valorant)
