// Figma -> normalized node JSON for FigmaBuild.lua. Run through the Figma MCP `use_figma` tool (Plugin API).
// Set ROOT_ID to the frame's node id (from the Figma URL ?node-id=12-345 -> "12:345") and PAGE to 0, 1, 2... :
// use_figma's output is capped at ~20 KB per call, so the tree is returned in pages of `chunk` characters; call again
// with the next PAGE until `done` is true, then join the pages in order (figma_to_luau.py --pages does that).
const ROOT_ID = "__ROOT_ID__";
const PAGE = __PAGE__;
const CHUNK = 18000;

const r3 = (v) => Math.round(v * 1000) / 1000;
const col = (c, a) => ({ r: r3(c.r), g: r3(c.g), b: r3(c.b), a: r3(a === undefined ? (c.a === undefined ? 1 : c.a) : a) });

function invert(m) { // 2x3 affine [[a,b,c],[d,e,f]] -> inverse
  const [[a, b, c], [d, e, f]] = m; const det = a * e - b * d;
  return [[e / det, -b / det, (b * f - c * e) / det], [-d / det, a / det, (c * d - a * f) / det]];
}
const apply = (m, x, y) => ({ x: r3(m[0][0] * x + m[0][1] * y + m[0][2]), y: r3(m[1][0] * x + m[1][1] * y + m[1][2]) });

function paint(p) {
  const o = { type: p.type, visible: p.visible !== false, opacity: r3(p.opacity === undefined ? 1 : p.opacity) };
  if (p.type === "SOLID") o.color = col(p.color, 1);
  if (p.type && p.type.startsWith("GRADIENT")) {
    o.stops = p.gradientStops.map((s) => ({ position: r3(s.position), color: col(s.color) }));
    const inv = invert(p.gradientTransform); // gradient space (0,.5)->(1,.5) back to the node's unit square
    o.handles = [apply(inv, 0, 0.5), apply(inv, 1, 0.5)];
  }
  if (p.type === "IMAGE") { o.scaleMode = p.scaleMode; o.imageHash = p.imageHash; }
  return o;
}

const CMAP = { MIN: "LEFT", MAX: "RIGHT", CENTER: "CENTER", STRETCH: "LEFT_RIGHT", SCALE: "SCALE" };
const VMAP = { MIN: "TOP", MAX: "BOTTOM", CENTER: "CENTER", STRETCH: "TOP_BOTTOM", SCALE: "SCALE" };

function walk(n) {
  const o = { id: n.id, name: n.name, type: n.type, x: r3(n.x || 0), y: r3(n.y || 0), w: r3(n.width || 0), h: r3(n.height || 0),
              visible: n.visible !== false };
  if ("opacity" in n && n.opacity < 1) o.opacity = r3(n.opacity);
  if ("rotation" in n && Math.abs(n.rotation) > 0.01) o.rotation = r3(n.rotation);
  if ("fills" in n && n.fills !== figma.mixed && n.fills.length) o.fills = n.fills.map(paint);
  if ("strokes" in n && n.strokes.length) {
    o.strokes = n.strokes.map(paint);
    o.strokeWeight = n.strokeWeight === figma.mixed ? (n.strokeTopWeight || 1) : n.strokeWeight;
    o.strokeAlign = n.strokeAlign;
  }
  if ("cornerRadius" in n) {
    if (n.cornerRadius === figma.mixed) o.radii = [n.topLeftRadius, n.topRightRadius, n.bottomRightRadius, n.bottomLeftRadius];
    else if (n.cornerRadius > 0) o.cornerRadius = n.cornerRadius;
  }
  if ("effects" in n && n.effects.length) o.effects = n.effects.map((e) => ({ type: e.type, visible: e.visible !== false,
    color: e.color ? col(e.color) : undefined, offset: e.offset, radius: e.radius, spread: e.spread }));
  if ("constraints" in n) o.constraints = { horizontal: CMAP[n.constraints.horizontal], vertical: VMAP[n.constraints.vertical] };
  if ("layoutMode" in n && n.layoutMode !== "NONE") {
    Object.assign(o, { layoutMode: n.layoutMode, itemSpacing: n.itemSpacing, primaryAlign: n.primaryAxisAlignItems,
      counterAlign: n.counterAxisAlignItems, wrap: n.layoutWrap === "WRAP",
      padding: { t: n.paddingTop, r: n.paddingRight, b: n.paddingBottom, l: n.paddingLeft } });
  }
  if ("layoutSizingHorizontal" in n) { o.sizingH = n.layoutSizingHorizontal; o.sizingV = n.layoutSizingVertical; }
  if ("layoutPositioning" in n && n.layoutPositioning === "ABSOLUTE") o.absolute = true;
  if ("clipsContent" in n && n.clipsContent) o.clips = true;
  if (n.type === "TEXT") {
    const fn = n.fontName === figma.mixed ? n.getRangeFontName(0, 1) : n.fontName;
    const lh = n.lineHeight === figma.mixed ? n.getRangeLineHeight(0, 1) : n.lineHeight;
    const fs = n.fontSize === figma.mixed ? n.getRangeFontSize(0, 1) : n.fontSize;
    const ls = n.letterSpacing === figma.mixed ? n.getRangeLetterSpacing(0, 1) : n.letterSpacing;
    o.text = { characters: n.characters, fontFamily: fn.family, italic: /italic/i.test(fn.style),
      fontWeight: n.fontWeight === figma.mixed ? 400 : n.fontWeight, fontSize: fs,
      lineHeightPx: lh.unit === "PIXELS" ? lh.value : (lh.unit === "PERCENT" ? fs * lh.value / 100 : undefined),
      letterSpacing: ls.unit === "PIXELS" ? ls.value : fs * ls.value / 100,
      alignH: n.textAlignHorizontal, alignV: n.textAlignVertical, autoResize: n.textAutoResize,
      textCase: n.textCase === figma.mixed ? "ORIGINAL" : n.textCase };
    if (n.fills === figma.mixed) o.fills = n.getRangeFills(0, 1).map(paint);
  }
  const bake = /_img$/.test(n.name);
  if ("children" in n && !bake) o.children = n.children.map(walk);
  return o;
}

const root = await figma.getNodeByIdAsync(ROOT_ID);
if (!root) throw new Error("node " + ROOT_ID + " not found");
const json = JSON.stringify(walk(root));
const pages = Math.ceil(json.length / CHUNK);
return { page: PAGE, pages, done: PAGE >= pages - 1, data: json.slice(PAGE * CHUNK, (PAGE + 1) * CHUNK) };
