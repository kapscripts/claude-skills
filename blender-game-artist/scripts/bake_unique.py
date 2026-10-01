"""Unique weathering bake: turns tiled / shared materials into one clean, non-repeating texture set per mesh.

What it does, per mesh object:
  1. adds a fresh UV map (smart project + pack, no overlaps, pixel margin) -> "UniqueUV"
  2. puts a weathering layer in front of every Principled BSDF: AO/cavity grime, ground dirt, rain streaks on walls,
     dust on upward faces, chipped edges (bevel-normal edge mask) and large-scale colour drift. All masks are driven
     by the mesh's own shape and world position, so no two walls get the same marks.
  3. bakes colour / roughness / metallic (emission trick) and a tangent normal map (keeps the tiled detail normals)
     into that UV map with Cycles
  4. (--apply) swaps the mesh to one baked material on UniqueUV and deletes the old UV maps, ready for glTF/FBX export
     -> one SurfaceAppearance per MeshPart in Roblox

usage (headless):
  blender -b scene.blend --python bake_unique.py -- --out C:/tmp/bake [--objects A,B | --collection Name]
          [--density 256] [--max 1024] [--min 128] [--samples 32] [--preset auto|plaster|concrete|metal|paint|wood|stone]
          [--strength 1.0] [--gpu] [--apply] [--save C:/tmp/baked.blend]
  or import a model first:  blender -b --factory-startup --python bake_unique.py -- --import asset.glb --out ...

Keep --out and --save paths short: Blender fails to write long Windows paths.
"""
import bpy, bmesh, math, os, sys, time

# ---------------------------------------------------------------------------------------------------------------- args
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None, flag=False):
    if flag:
        return f"--{name}" in argv
    return argv[argv.index(f"--{name}") + 1] if f"--{name}" in argv else default

OUT = arg("out", os.path.join(os.environ.get("TEMP", "/tmp"), "bake_unique"))
DENSITY = float(arg("density", 256))       # pixels per metre before clamping
RES_MAX = int(arg("max", 1024))            # Roblox SurfaceAppearance caps at 1024
RES_MIN = int(arg("min", 128))
SAMPLES = int(arg("samples", 32))
PRESET = arg("preset", "auto")
STRENGTH = float(arg("strength", 1.0))     # scales every weathering amount
MARGIN = int(arg("margin", 8))             # px bleed so mip-maps don't show seams
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------------------------------------------------- presets
# grime: AO/cavity dirt   ground: dirt band height (m)   streak: rain streaks on vertical faces   dust: on up faces
# wear: edge chipping amount   wear_col: what shows through chipped edges   wear_metal: metallic of exposed edges
# drift: large-scale value variation   dirt: dirt colour (linear)
PRESETS = {
    "plaster":  dict(grime=.55, ground=1.4, streak=.45, dust=.25, wear=.35, wear_col=(.55, .50, .44), wear_metal=0, drift=.12, dirt=(.20, .17, .13)),
    "concrete": dict(grime=.60, ground=1.0, streak=.55, dust=.30, wear=.25, wear_col=(.45, .44, .42), wear_metal=0, drift=.10, dirt=(.14, .13, .12)),
    "metal":    dict(grime=.50, ground=.8,  streak=.40, dust=.20, wear=.55, wear_col=(.28, .27, .26), wear_metal=1, drift=.08, dirt=(.18, .10, .05)),
    "paint":    dict(grime=.45, ground=.8,  streak=.35, dust=.20, wear=.60, wear_col=(.30, .29, .28), wear_metal=1, drift=.08, dirt=(.16, .11, .07)),
    "wood":     dict(grime=.50, ground=.7,  streak=.30, dust=.25, wear=.40, wear_col=(.42, .34, .24), wear_metal=0, drift=.14, dirt=(.12, .09, .06)),
    "stone":    dict(grime=.55, ground=1.0, streak=.35, dust=.30, wear=.20, wear_col=(.50, .47, .42), wear_metal=0, drift=.12, dirt=(.15, .13, .10)),
    "clean":    dict(grime=.25, ground=.4,  streak=.10, dust=.10, wear=.10, wear_col=(.50, .50, .50), wear_metal=0, drift=.05, dirt=(.20, .18, .16)),
}
KEYWORDS = [("metal", ("iron", "steel", "rust", "corrugat", "container", "plate", "graphite", "cladding", "metal")),
            ("paint", ("paint", "sign", "hazard", "shutter")),
            ("wood", ("wood", "plank")),
            ("concrete", ("concrete", "asphalt", "paving", "stain", "soot")),
            ("stone", ("stone", "tuff", "brick", "rock", "terracotta")),
            ("clean", ("glass", "lens", "light", "emissive", "foliage", "leaf"))]

def preset_for(mat):
    if PRESET != "auto":
        return PRESETS[PRESET]
    n = mat.name.lower()
    for key, words in KEYWORDS:
        if any(w in n for w in words):
            return PRESETS[key]
    return PRESETS["plaster"]

# ---------------------------------------------------------------------------------------------------------- node utils
def N(nt, kind, x=0, y=0, **props):
    n = nt.nodes.new(kind)
    n.location = (x, y)
    for k, v in props.items():
        setattr(n, k, v)
    return n

def mix_col(nt, fac, a, b, blend="MIX"):
    m = N(nt, "ShaderNodeMix", data_type="RGBA", blend_type=blend)
    link(nt, fac, m.inputs[0]); link(nt, a, m.inputs[6]); link(nt, b, m.inputs[7])
    return m.outputs[2]

def math_(nt, op, a, b=None, clamp=False):
    m = N(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
    link(nt, a, m.inputs[0])
    if b is not None:
        link(nt, b, m.inputs[1])
    return m.outputs[0]

def ramp(nt, v, lo, hi):
    m = N(nt, "ShaderNodeMapRange", clamp=True)
    link(nt, v, m.inputs["Value"]); m.inputs["From Min"].default_value = lo; m.inputs["From Max"].default_value = hi
    return m.outputs["Result"]

def link(nt, src, dst):
    """src: output socket or plain value/tuple; dst: input socket"""
    if hasattr(src, "is_output"):
        nt.links.new(src, dst)
    else:
        dst.default_value = src

def source(nt, sock):
    """what currently feeds an input socket: the linked output or the socket's constant"""
    if sock.is_linked:
        return sock.links[0].from_socket
    v = sock.default_value
    return tuple(v) if hasattr(v, "__len__") else v

def noise(nt, vec, scale, detail=4.0, rough=.55, stretch=None):
    if stretch:  # anisotropic noise (rain streaks): squash the coordinate on one axis
        vm = N(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); link(nt, vec, vm.inputs[0]); vm.inputs[1].default_value = stretch
        vec = vm.outputs[0]
    n = N(nt, "ShaderNodeTexNoise"); link(nt, vec, n.inputs["Vector"])
    n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
    return n.outputs["Fac"]

# ------------------------------------------------------------------------------------------------------ weathering layer
def weather(mat):
    """insert the weathering layer between the material's sources and its Principled BSDF (once per material)"""
    if mat.get("bu_weathered") or mat.node_tree is None:
        return
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    p = preset_for(mat); s = STRENGTH
    # pin every image texture without a vector input to the ORIGINAL uv map, so the tiled base keeps its mapping
    uv0 = mat.get("bu_uv0")
    if uv0:
        for img in [n for n in nt.nodes if n.type == "TEX_IMAGE" and not n.inputs["Vector"].is_linked]:
            uvn = N(nt, "ShaderNodeUVMap", uv_map=uv0); nt.links.new(uvn.outputs["UV"], img.inputs["Vector"])
    base_col = source(nt, bsdf.inputs["Base Color"])
    base_rough = source(nt, bsdf.inputs["Roughness"])
    base_metal = source(nt, bsdf.inputs["Metallic"])

    geo = N(nt, "ShaderNodeNewGeometry")
    tex = N(nt, "ShaderNodeTexCoord")
    wpos = geo.outputs["Position"]                       # world space: every copy / wall gets different marks
    sep = N(nt, "ShaderNodeSeparateXYZ"); link(nt, geo.outputs["Normal"], sep.inputs[0])
    up = sep.outputs["Z"]                                # 1 = faces up, 0 = wall, -1 = underside
    seppos = N(nt, "ShaderNodeSeparateXYZ"); link(nt, wpos, seppos.inputs[0])
    gz = N(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="bu_ground_z").outputs["Fac"]
    height = math_(nt, "SUBTRACT", seppos.outputs["Z"], gz)

    # cavity / contact grime from ambient occlusion
    ao = N(nt, "ShaderNodeAmbientOcclusion", samples=16, only_local=False); ao.inputs["Distance"].default_value = .6
    cav = math_(nt, "SUBTRACT", 1.0, ao.outputs["AO"], clamp=True)
    breakup = ramp(nt, noise(nt, wpos, 3.0, 6, .65), .35, .75)
    grime = math_(nt, "MULTIPLY", ramp(nt, cav, .05, .6), math_(nt, "ADD", .35, breakup), clamp=True)
    # ground dirt band, ragged top edge
    gband = math_(nt, "SUBTRACT", 1.0, ramp(nt, math_(nt, "ADD", height, math_(nt, "MULTIPLY", noise(nt, wpos, 1.5), .6)), 0, p["ground"]), clamp=True)
    grime = math_(nt, "MAXIMUM", grime, math_(nt, "MULTIPLY", gband, .8))
    # rain streaks: vertically stretched noise, only on walls, stronger near the top of each wall run
    wall = math_(nt, "SUBTRACT", 1.0, math_(nt, "ABSOLUTE", up), clamp=True)
    streak = ramp(nt, noise(nt, wpos, 4.0, 3, .5, stretch=(1.0, 1.0, .06)), .52, .72)
    streak = math_(nt, "MULTIPLY", streak, ramp(nt, wall, .6, .95))
    grime = math_(nt, "MAXIMUM", grime, math_(nt, "MULTIPLY", streak, p["streak"] / max(p["grime"], .01)))
    grime = math_(nt, "MULTIPLY", grime, p["grime"] * s, clamp=True)
    # dust settles on up-facing surfaces
    dust = math_(nt, "MULTIPLY", ramp(nt, up, .55, .95), ramp(nt, noise(nt, wpos, 2.2, 5), .35, .65))
    dust = math_(nt, "MULTIPLY", dust, p["dust"] * s, clamp=True)
    # edge wear: bevel-shader normal vs true normal lights up hard convex+concave edges; AO removes the concave ones
    bev = N(nt, "ShaderNodeBevel", samples=8); bev.inputs["Radius"].default_value = .025
    dot = N(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT"); link(nt, bev.outputs["Normal"], dot.inputs[0]); link(nt, geo.outputs["Normal"], dot.inputs[1])
    edge = ramp(nt, math_(nt, "SUBTRACT", 1.0, dot.outputs["Value"]), .004, .06)
    edge = math_(nt, "MULTIPLY", edge, ramp(nt, ao.outputs["AO"], .55, .85))          # convex only
    chips = ramp(nt, noise(nt, wpos, 14.0, 8, .7), .42, .6)
    wear = math_(nt, "MULTIPLY", math_(nt, "MULTIPLY", edge, chips), p["wear"] * s * 1.6, clamp=True)
    # large-scale colour drift (sun fade / patchy repaint)
    drift = math_(nt, "ADD", math_(nt, "MULTIPLY", math_(nt, "SUBTRACT", noise(nt, wpos, .12, 2), .5), p["drift"] * 2 * s), 1.0)

    col = mix_col(nt, 1.0, base_col, drift, "MULTIPLY")                       # float socket -> grey colour
    col = mix_col(nt, math_(nt, "MULTIPLY", ramp(nt, cav, .1, .7), .25 * s, clamp=True), col, (0, 0, 0, 1))  # mild AO tone
    col = mix_col(nt, grime, col, (*p["dirt"], 1), "MULTIPLY")
    col = mix_col(nt, math_(nt, "MULTIPLY", grime, .45), col, (*p["dirt"], 1))
    col = mix_col(nt, dust, col, (.52, .48, .42, 1))
    col = mix_col(nt, wear, col, (*p["wear_col"], 1))
    link(nt, col, bsdf.inputs["Base Color"])

    rough = math_(nt, "ADD", base_rough, math_(nt, "SUBTRACT", math_(nt, "MULTIPLY", grime, .15), math_(nt, "MULTIPLY", wear, .25)), clamp=True)
    rough = math_(nt, "ADD", rough, math_(nt, "MULTIPLY", dust, .2), clamp=True)
    link(nt, rough, bsdf.inputs["Roughness"])
    if p["wear_metal"]:
        metal = math_(nt, "ADD", base_metal, math_(nt, "MULTIPLY", wear, p["wear_metal"]), clamp=True)
        metal = math_(nt, "MULTIPLY", metal, math_(nt, "SUBTRACT", 1.0, grime), clamp=True)
        link(nt, metal, bsdf.inputs["Metallic"])
    mat["bu_weathered"] = 1

# ------------------------------------------------------------------------------------------------------------ uv + bake
def unique_uv(ob):
    me = ob.data
    if "UniqueUV" in me.uv_layers:
        return
    uv0 = me.uv_layers.active.name if me.uv_layers.active else None
    for m in me.materials:
        if m and uv0:
            m["bu_uv0"] = uv0
    if len(me.uv_layers) >= 8:
        me.uv_layers.remove(me.uv_layers[-1])
    uv = me.uv_layers.new(name="UniqueUV")
    me.uv_layers.active = uv                                # bake target = active (not render) uv map
    if uv0:
        me.uv_layers[uv0].active_render = True              # tiled base textures still read the old map
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.003, area_weight=0, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=.004)
    bpy.ops.object.mode_set(mode="OBJECT")

def surface_area(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    a = sum(f.calc_area() for f in bm.faces); bm.free()
    return a

def res_for(ob):
    side = math.sqrt(max(surface_area(ob), 1e-4)) * DENSITY
    r = 2 ** round(math.log2(max(side, 1)))
    return int(min(RES_MAX, max(RES_MIN, r)))

def bake_object(ob):
    res = res_for(ob)
    mats = [m for m in ob.data.materials if m]
    imgs = {}
    for ch, noncolor in (("color", False), ("roughness", True), ("metalness", True), ("normal", True)):
        im = bpy.data.images.new(f"{ob.name}_{ch}", res, res, alpha=False, float_buffer=False)
        if noncolor:
            im.colorspace_settings.name = "Non-Color"
        imgs[ch] = im
    target_nodes = {}
    for m in mats:
        tn = m.node_tree.nodes.new("ShaderNodeTexImage"); tn.name = "bu_target"; target_nodes[m] = tn
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bk = bpy.context.scene.render.bake
    bk.margin = MARGIN; bk.margin_type = "EXTEND"; bk.use_clear = True; bk.target = "IMAGE_TEXTURES"

    def point(ch):
        for m, tn in target_nodes.items():
            tn.image = imgs[ch]; m.node_tree.nodes.active = tn

    # colour / roughness / metallic: route each BSDF input through an emission shader, bake EMIT
    for ch, sock in (("color", "Base Color"), ("roughness", "Roughness"), ("metalness", "Metallic")):
        saved = []
        for m in mats:
            nt = m.node_tree
            out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
            bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if out is None:
                continue
            old = out.inputs["Surface"].links[0].from_socket if out.inputs["Surface"].is_linked else None
            em = nt.nodes.new("ShaderNodeEmission"); em.name = "bu_emit"
            if bsdf is not None:
                src = source(nt, bsdf.inputs[sock])
                if not hasattr(src, "is_output"):
                    src = (src, src, src, 1) if isinstance(src, float) else src
                link(nt, src, em.inputs["Color"])
            nt.links.new(em.outputs[0], out.inputs["Surface"])
            saved.append((nt, out, old, em))
        point(ch)
        bpy.ops.object.bake(type="EMIT")
        for nt, out, old, em in saved:
            nt.nodes.remove(em)
            if old is not None:
                nt.links.new(old, out.inputs["Surface"])
    point("normal")
    bk.normal_space = "TANGENT"
    bpy.ops.object.bake(type="NORMAL")

    paths = {}
    for ch, im in imgs.items():
        p = os.path.join(OUT, f"{ob.name}_{ch}.png"); im.filepath_raw = p; im.file_format = "PNG"; im.save(); paths[ch] = p
    for m, tn in target_nodes.items():
        m.node_tree.nodes.remove(tn)
    return res, imgs

def apply_baked(ob, imgs):
    """one baked material on UniqueUV, old uv maps removed (glTF exports TEXCOORD_0 from the first map)"""
    mat = bpy.data.materials.new(f"{ob.name}_Baked"); nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    def img(ch):
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = imgs[ch]; return n.outputs["Color"]
    nt.links.new(img("color"), bsdf.inputs["Base Color"])
    nt.links.new(img("roughness"), bsdf.inputs["Roughness"])
    nt.links.new(img("metalness"), bsdf.inputs["Metallic"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(img("normal"), nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    ob.data.materials.clear(); ob.data.materials.append(mat)
    for uv in [u for u in ob.data.uv_layers if u.name != "UniqueUV"]:
        ob.data.uv_layers.remove(uv)
    ob.data.uv_layers["UniqueUV"].active = True; ob.data.uv_layers["UniqueUV"].active_render = True

# ----------------------------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    if arg("import"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = arg("import")
        (bpy.ops.import_scene.gltf(filepath=path) if path.lower().endswith((".glb", ".gltf")) else bpy.ops.import_scene.fbx(filepath=path))
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = False
    if arg("gpu", flag=True):
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
            try:
                prefs.compute_device_type = kind; prefs.get_devices()
                if any(d.type == kind for d in prefs.devices):
                    for d in prefs.devices: d.use = True
                    sc.cycles.device = "GPU"; break
            except TypeError:
                pass
    if arg("objects"):
        obs = [bpy.data.objects[n] for n in arg("objects").split(",")]
    elif arg("collection"):
        obs = list(bpy.data.collections[arg("collection")].all_objects)
    else:
        obs = list(sc.objects)
    obs = [o for o in obs if o.type == "MESH" and o.data.polygons and "guide" not in o.name.lower() and "collider" not in o.name.lower()]
    # one ground height for the whole asset (lowest world vertex): dirt bands line up across every piece
    gz = min(min((o.matrix_world @ v.co).z for v in o.data.vertices) for o in obs)
    if arg("ground_z") is not None:
        gz = float(arg("ground_z"))
    for o in obs:
        o["bu_ground_z"] = gz
        if o.data.users > 1:
            o.data = o.data.copy()   # instanced meshes would share one UV layout / texture
    for o in obs:
        unique_uv(o)
    for m in {m for o in obs for m in o.data.materials if m}:
        weather(m)
    report = []
    for i, o in enumerate(obs):
        t = time.time()
        res, imgs = bake_object(o)
        report.append((o.name, res))
        print(f"[{i + 1}/{len(obs)}] {o.name}: {res}px in {time.time() - t:.1f}s", flush=True)
        if arg("apply", flag=True):
            apply_baked(o, imgs)
    if arg("save"):
        bpy.ops.wm.save_as_mainfile(filepath=arg("save"))
    px = sum(r * r for _, r in report)
    print(f"done: {len(report)} meshes, {px / 1e6:.1f} Mpx of colour maps (~{px * 4 * 4 * 1.33 / 2**20:.0f} MB RGBA+mips for 4 maps),"
          f" {time.time() - t0:.0f}s -> {OUT}", flush=True)

main()
