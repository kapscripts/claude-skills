"""Figma frame -> one Luau chunk that builds it as real Roblox GUI instances (run it with the Roblox Studio MCP
`execute_luau`, or paste it into the Studio command bar).

Inputs (pick one):
  --pages p0.txt p1.txt ...   the `data` strings returned by figma_walker.js page by page (joined in order)
  --tree tree.json            an already-normalized tree (the joined walker output)
  --rest nodes.json [--node 12:345]   Figma REST response (GET /v1/files/:key/nodes?ids=... or /v1/files/:key)
Options:
  --assets assets.json   {"<nodeId>": "rbxassetid://123", ...} from uploading image fills and *_img layers
  --parent EXPR          Luau expression for the parent, default nil (builds a detached preview that changes nothing)
  --screengui            wrap the root frame in a ScreenGui (ResetOnSpawn false, Sibling ZIndex, safe insets)
  --name NAME            ScreenGui name (default: the frame's name)
  --no-scale-root        root = full-screen Scale frame instead of design-size frame + UIScale (see SKILL.md)
  --out file.lua         default: stdout

usage: python figma_to_luau.py --pages page0.txt page1.txt --assets assets.json --screengui --out build.lua
"""
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rest_normalize(n, parent_box=None):
    """Figma REST node -> the walker's normalized schema (positions relative to the parent)."""
    box = n.get("absoluteBoundingBox") or {"x": 0, "y": 0, "width": 0, "height": 0}
    px, py = (parent_box["x"], parent_box["y"]) if parent_box else (box["x"], box["y"])
    o = {"id": n["id"], "name": n.get("name", ""), "type": n["type"], "x": box["x"] - px, "y": box["y"] - py,
         "w": box["width"], "h": box["height"], "visible": n.get("visible", True)}
    if n.get("opacity", 1) < 1:
        o["opacity"] = n["opacity"]

    def paint(p):
        q = {"type": p["type"], "visible": p.get("visible", True), "opacity": p.get("opacity", 1)}
        if p["type"] == "SOLID":
            q["color"] = p["color"]
        if p["type"].startswith("GRADIENT"):
            q["stops"] = [{"position": s["position"], "color": s["color"]} for s in p.get("gradientStops", [])]
            h = p.get("gradientHandlePositions") or []
            if len(h) >= 2:
                q["handles"] = [h[0], h[1]]
        if p["type"] == "IMAGE":
            q["scaleMode"] = p.get("scaleMode")
            q["imageRef"] = p.get("imageRef")
        return q

    if n.get("fills"):
        o["fills"] = [paint(p) for p in n["fills"]]
    if n.get("strokes"):
        o["strokes"] = [paint(p) for p in n["strokes"]]
        o["strokeWeight"] = n.get("strokeWeight", 1)
        o["strokeAlign"] = n.get("strokeAlign", "INSIDE")
    if n.get("rectangleCornerRadii"):
        o["radii"] = n["rectangleCornerRadii"]
    elif n.get("cornerRadius"):
        o["cornerRadius"] = n["cornerRadius"]
    if n.get("effects"):
        o["effects"] = [{"type": e["type"], "visible": e.get("visible", True), "color": e.get("color"),
                         "offset": e.get("offset"), "radius": e.get("radius"), "spread": e.get("spread", 0)}
                        for e in n["effects"]]
    if n.get("constraints"):
        o["constraints"] = n["constraints"]
    if n.get("layoutMode") and n["layoutMode"] != "NONE":
        o.update(layoutMode=n["layoutMode"], itemSpacing=n.get("itemSpacing", 0),
                 primaryAlign=n.get("primaryAxisAlignItems", "MIN"), counterAlign=n.get("counterAxisAlignItems", "MIN"),
                 wrap=n.get("layoutWrap") == "WRAP",
                 padding={"t": n.get("paddingTop", 0), "r": n.get("paddingRight", 0),
                          "b": n.get("paddingBottom", 0), "l": n.get("paddingLeft", 0)})
    if n.get("layoutSizingHorizontal"):
        o["sizingH"], o["sizingV"] = n["layoutSizingHorizontal"], n.get("layoutSizingVertical")
    if n.get("layoutPositioning") == "ABSOLUTE":
        o["absolute"] = True
    if n.get("clipsContent"):
        o["clips"] = True
    if n["type"] == "TEXT":
        s = n.get("style", {})
        o["text"] = {"characters": n.get("characters", ""), "fontFamily": s.get("fontFamily"), "italic": s.get("italic", False),
                     "fontWeight": s.get("fontWeight", 400), "fontSize": s.get("fontSize", 14),
                     "lineHeightPx": s.get("lineHeightPx"), "letterSpacing": s.get("letterSpacing", 0),
                     "alignH": s.get("textAlignHorizontal", "LEFT"), "alignV": s.get("textAlignVertical", "TOP"),
                     "autoResize": s.get("textAutoResize", "NONE"), "textCase": s.get("textCase", "ORIGINAL")}
    if n.get("children") and not o["name"].endswith("_img"):
        o["children"] = [rest_normalize(c, box) for c in n["children"]]
    return o


def load_tree(a):
    if a.pages:
        return json.loads("".join(open(p, encoding="utf-8").read() for p in a.pages))
    if a.tree:
        return json.load(open(a.tree, encoding="utf-8"))
    doc = json.load(open(a.rest, encoding="utf-8"))
    if "nodes" in doc:  # /nodes response
        key = a.node or next(iter(doc["nodes"]))
        node = doc["nodes"][key]["document"]
    else:
        node = doc["document"]
        if a.node:
            stack = [node]
            while stack:
                cur = stack.pop()
                if cur.get("id") == a.node:
                    node = cur
                    break
                stack.extend(cur.get("children", []))
    return rest_normalize(node)


def count(n):
    return 1 + sum(count(c) for c in n.get("children", []))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pages", nargs="+")
    g.add_argument("--tree")
    g.add_argument("--rest")
    ap.add_argument("--node")
    ap.add_argument("--assets")
    ap.add_argument("--parent", default="nil")
    ap.add_argument("--screengui", action="store_true")
    ap.add_argument("--name")
    ap.add_argument("--no-scale-root", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()

    tree = load_tree(a)
    assets = json.load(open(a.assets)) if a.assets else {}
    tree_json = json.dumps(tree, separators=(",", ":"))
    lvl = 2
    while f"]{'=' * lvl}]" in tree_json:
        lvl += 1
    eq = "=" * lvl
    builder = open(os.path.join(HERE, "FigmaBuild.lua"), encoding="utf-8").read()
    opts = {"screenGui": a.screengui, "scaleRoot": not a.no_scale_root}
    if a.name:
        opts["name"] = a.name
    lua = (builder + "\n\nlocal tree = HttpService:JSONDecode([" + eq + "[" + tree_json + "]" + eq + "])\n"
           "local assetMap = HttpService:JSONDecode([==[" + json.dumps(assets) + "]==])\n"
           "local opts = HttpService:JSONDecode([==[" + json.dumps(opts) + "]==])\n"
           f"opts.parent = {a.parent}\n"
           "local root, report = FigmaBuild(tree, assetMap, opts)\n"
           "return root:GetFullName() .. ' | ' .. report\n")
    if a.out:
        open(a.out, "w", encoding="utf-8").write(lua)
    else:
        sys.stdout.write(lua)
    print(f"{count(tree)} Figma nodes -> {len(lua) / 1024:.0f} KB Luau"
          + (f" -> {a.out}" if a.out else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
