# Review: critique, audit, polish and harden

## Critique (design review, no edits)

Evidence first. Capture the screen in Studio at phone, 1080p and console sizes (plus the Figma frame if there is one).

1. **Specificity verdict:** could an unrelated game use this screen unchanged? If yes, that is the top issue.
2. **Squint test and hierarchy:** is the primary element obvious, groups clear, and the reading order right?
3. **Cognitive load:** count the visible choices at each decision point.
   - ≤ 4 is fine.
   - 5–7 needs grouping or progressive disclosure.
   - 8 or more is overloaded.
4. **Heuristics:** score each 0–4 (0 = absent or broken, 4 = excellent), with one finding each.
   1. Visibility of state (does every action confirm? is progress shown?)
   2. Match with the game's world and language
   3. Player control (back, cancel, undo, escape)
   4. Consistency (same patterns and colours everywhere)
   5. Error prevention (confirm destructive actions such as "Scrap item")
   6. Recognition over recall (icons plus labels, visible stats)
   7. Efficiency (shortcuts, bulk actions, remembered filters)
   8. Aesthetic and minimal (no noise, one focal point)
   9. Error recovery (clear messages with fixes)
   10. Help (tooltips, first-time hints)
5. **Game-feel checks:**
   - feedback latency under 100 ms;
   - a sound on every state change;
   - motion that fits the fiction;
   - reward moments that scale with importance.
6. **Report:**
   - overall impression;
   - what works;
   - **priority issues** P0–P3, each with *what*, *why it matters*, a concrete *fix*, and the command that would address
     it;
   - persona red flags: a new player on a phone, a veteran on PC, a console player on a couch;
   - minor notes.

## Audit (technical)

Check each item and record evidence (a property value or a screenshot):

- **Scaling:**
  - one UIScale fit, or deliberate Scale use;
  - no clipped or overflowing text at 844×390 or at 4K;
  - AnchorPoints correct at every edge.
- **Safe areas:**
  - ScreenInsets set;
  - nothing under the 58 px top bar or a notch;
  - bottom corners on phone clear of the thumbstick and jump button.
- **Text:**
  - no TextScaled next to other text;
  - sizes at or above the platform minimums;
  - contrast 4.5:1, or 3:1 for large text;
  - readable over the brightest world scene;
  - +40% localisation doesn't break the layout.
- **Input:**
  - touch targets ≥ 44–48 px effective;
  - gamepad: a default selection on open, a sensible NextSelection path, focus trapped in modals, visible custom focus;
  - B/back closes;
  - keyboard shortcuts shown on PC.
- **States:** idle, hover, press, focus and disabled on every control; loading, empty and error on every data view.
- **Performance:**
  - fast-updating elements in their own ScreenGui;
  - instance count reasonable;
  - no per-frame work while hidden;
  - CanvasGroups temporary;
  - strokes under ~300 and shadows under ~100;
  - images sized to their display size, and icons in an atlas.
- **Accessibility:**
  - ReducedMotion respected;
  - colour never the only cue;
  - PreferredTextSize considered.
- **Hygiene:**
  - meaningful instance names;
  - no leftover debug frames;
  - connections cleaned up on destroy;
  - shared UI changes synced to every place that uses them.

## Polish (final pass; refine, never secretly redesign)

Triage in this order:
1. broken or blocked flows and misleading state;
2. missing states;
3. hierarchy, layout and consistency drift;
4. visual and motion inconsistencies;
5. cleanup.

Then:
- Align everything to the grid and the 4 px spacing scale, and fix optical alignment (icons next to text, numbers in
  columns).
- Make same-role text identical everywhere.
- Use one icon family and weight, and keep colour meanings consistent.
- Check every tiered or quantity illustration: its bounding-box centre sits on the card centre (compute it, don't eyeball it),
  it clears badges and labels, lower tiers use symmetric currency groups (1 → pair → pyramid, never a lopsided extra
  copy), and the top tier has a different, bigger accent icon with nothing outside it.
- Check that the icons are all Lucide, apart from brand marks (Robux) and the game's currency icon, and that each one fits
  its meaning without reading as a UI verb.
- **Run the anti-flat lint** (below) before every screenshot you show the user, and fix everything it flags:
  - subtext spam;
  - strokes under 2 px;
  - flat panels;
  - one shape taking more than 75% of the containers;
  - floating boxes;
  - labels off-centre by more than 1 px (see the alignment check below).
- Put every control through all its states, with mouse, touch and gamepad.
- Put motion timing on the tokens: exits faster than entrances, nothing longer than it needs to be, interruptible.
- Add a sound hook to every meaningful state change.
- Re-verify in the Device emulator at all sizes. Two inspection rounds at most, then ship.

## Harden (edge cases)

- **Content extremes:**
  - long names (20+ characters, and localised);
  - 0, 1 and 999,999+ counts;
  - a full or empty inventory;
  - many notifications at once (queue and cap them);
  - missing images (a placeholder, not a blank).
- **Timing:**
  - slow server responses (show pending state, block double submits);
  - the player dying or teleporting while a menu is open;
  - opening or closing while an animation is still running (state machines);
  - respawn with `ResetOnSpawn` behaviour.
- **Errors:** purchase failures, trade declines, disconnects, full inventory on pickup. Each needs clear copy and a
  recovery path.
- **Platform switches** mid-session: plugging in a gamepad, rotating the phone, resizing the window.

## Anti-flat lint (run with use_figma on the frame; set ROOT)

```js
const ROOT='23:2'; const root=await figma.getNodeByIdAsync(ROOT);
const out={hairlines:0,subtext:[],flat:[],shapes:{},floating:[]};
const isImgOrGrad=f=>f.type==='IMAGE'||f.type.startsWith('GRADIENT');
for(const n of root.findAll(()=>true)){
  if(!n.visible) continue;
  if('strokes' in n && n.strokes.length && typeof n.strokeWeight==='number' && n.strokeWeight<2) out.hairlines++;
  if(n.type==='TEXT' && typeof n.fontSize==='number' && n.fontSize<=22 && n.characters.split(' ').length>=3) out.subtext.push(n.characters.slice(0,40));
  const box=(n.type==='FRAME'||n.type==='RECTANGLE')&&n.width>=120&&n.height>=60;
  if(box&&n.width>=200&&n.height>=120&&n.fills.length===1&&n.fills[0].type==='SOLID'
     &&!(n.children||[]).some(c=>c.fills&&c.fills.some&&c.fills.some(isImgOrGrad))) out.flat.push(n.name);
  // shape vocabulary: containers bucketed by corner treatment
  if(box&&n.fills&&n.fills.length){const r=typeof n.cornerRadius==='number'?n.cornerRadius:'mixed';
    const k=n.rotation?'rotated':(r==='mixed'?'asym':(r>=Math.min(n.width,n.height)/2-1?'pill':r>0?'round'+Math.round(r/8)*8:'square'));
    out.shapes[k]=(out.shapes[k]||0)+1;}
  if(['STAR','POLYGON','ELLIPSE'].includes(n.type)&&n.width>=40) out.shapes[n.type]=(out.shapes[n.type]||0)+1;
  // floating: a filled container whose parent is the screen root and which touches no edge/neighbour alignment
  if(box&&n.parent===root&&n.fills&&n.fills.length){const W=root.width,Hh=root.height,m=48;
    const nearEdge=n.x<=m||n.y<=m||W-(n.x+n.width)<=m||Hh-(n.y+n.height)<=m;
    const aligned=root.children.some(o=>o!==n&&o.width>=120&&(Math.abs(o.x-n.x)<2||Math.abs(o.y-n.y)<2||Math.abs(o.x+o.width-n.x-n.width)<2||Math.abs(o.y+o.height-n.y-n.height)<2));
    const centred=Math.abs(n.x+n.width/2-W/2)<4&&Math.abs(n.y+n.height/2-Hh/2)<40;
    if(!nearEdge&&!aligned&&!centred) out.floating.push(n.name);}
}
const total=Object.values(out.shapes).reduce((a,b)=>a+b,0), top=Math.max(0,...Object.values(out.shapes));
return {hairlines:out.hairlines, subtext:out.subtext, flatPanels:out.flat, shapes:out.shapes,
  oneShapeShare:total?Math.round(top/total*100)+'%':'-', floating:out.floating};
```

Gotchas: mixed-style text makes `fontSize`/`fontName` a symbol (guard with typeof, load with getRangeAllFontNames); compare
positions in one space (absoluteTransform), never a child's x/y against an absolute value.

Pass criteria (read them through the screen's register, SKILL.md Rule 3: short hype badges are fine in casual and
in-world stat labels are fine in info-dense; sentences of explanation are never fine):
- `hairlines` = 0.
- `subtext` has at most 1 entry, and only a decision-changing one. Sentences of 3+ words at ≤ 22 px are probable
  subtext.
- `flatPanels` is empty, unless one is a deliberate plain surface under a hero image. Otherwise give it a gradient base
  and a texture layer (craft.md §9.3).
- `oneShapeShare` ≤ 75%, and the accent and focus shapes from craft.md §9.7 are present.
- `floating` is empty (anchor it to an edge, the grid or its subject, craft.md §9.8).

## Alignment check (run after every layout pass; set ROOT)

```js
const ROOT='23:2'; const root=await figma.getNodeByIdAsync(ROOT);
for(const t of root.findAll(n=>n.type==='TEXT')) for(const f of t.getRangeAllFontNames(0,t.characters.length)) await figma.loadFontAsync(f); // mixed-style text safe
function ink(t,str){const c=t.clone();figma.currentPage.appendChild(c);c.strokes=[];c.effects=[];if(str)c.characters=str;
  c.x=0;c.y=-5000;const b=c.absoluteRenderBounds;const r={l:b.x-c.x,t:b.y-c.y,w:b.width,h:b.height};c.remove();return r;}
const bad=[];
for(const b of root.findAll(n=>n.type==='FRAME'&&n.name.endsWith('_btn'))){
  const lab=b.findOne(c=>c.name==='Label'), face=b.findOne(c=>c.name==='Face'); if(!lab||!face) continue;
  const t=lab.findOne(c=>c.type==='TEXT'), ic=lab.findOne(c=>/robux|Icon_/.test(c.name)&&c!==t); if(!t) continue;
  const kc=ink(t,'H0'), k=ink(t), sw=b.strokeWeight||0, faceCy=(sw+face.height)/2;
  const inkCy=t.y+kc.t+kc.h/2, groupL=Math.min(ic?ic.x:1e9,t.x+k.l), groupR=t.x+k.l+k.w, groupCx=(groupL+groupR)/2;
  const e={btn:b.name,font:t.fontSize,dy:+(inkCy-faceCy).toFixed(1),dx:+(groupCx-b.width/2).toFixed(1),
    iconDy:ic?+((ic.y+ic.height/2)-inkCy).toFixed(1):0,padL:Math.round(groupL-sw),capH:Math.round(kc.h)};
  if(Math.abs(e.dy)>1||Math.abs(e.dx)>1||Math.abs(e.iconDy)>1||e.padL<e.capH) bad.push(e);
}
return {offenders:bad};
```

It must return no offenders. Also compare sibling groups: every `font` value within a group (price pills, tabs, CTAs of
the same height) must be identical.

Extra checks from the fix reference (craft.md §9.10). All must pass:
- **Icon-only buttons:** `glyph = iconFrame.children.at(-1)`. Compare the centre of `glyph.absoluteRenderBounds` with the
  face centre (x = w/2, y = (stroke + faceH)/2). Allowed: ±1 px.
- **Stacked text:** `gap = nextTop − (name.y + ink(name,'Hgjpqy').bottom + name.strokeWeight)`. Allowed: ≥ 8 px. The group
  centre must be within 1 px of the row centre.
- **Numbers:** fill vs outline ≥ 7:1 and outline vs face ≥ 4.5:1 (WCAG luminance). The price, count and timer treatments
  must be identical.
- **Icon + outlined text:** the gap from the icon edge to the text outline edge must equal 0.32 × cap (±1).
