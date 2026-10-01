"""Mid-poly finish: rounded, light-catching edges on hard-surface meshes at game-friendly triangle counts.

Adds (or with --apply, applies) the standard pro stack to each mesh:
  smooth shading -> Bevel (angle-limited, 1-3 segments, Harden Normals) -> Weighted Normal (face area, Keep Sharp)
  -> Triangulate (keeps custom normals, so Roblox/glTF get exactly the shading Blender shows)
and prints the triangle count per mesh against the Roblox 20k per-mesh limit.

usage:
  blender -b scene.blend --python midpoly.py -- [--objects A,B | --collection Name] [--width 0.012] [--segments 2]
          [--angle 30] [--apply] [--save out.blend]
  inside a live Blender (MCP execute_blender_code): exec(open(r"<path>/midpoly.py").read()) with sys.argv unchanged
  runs on the selected meshes.

Width is in metres: 0.005-0.02 for props, 0.02-0.05 for building edges. Segments 1-2 for anything seen from >5 m, 3 for hero
props held in hand. More segments than that are wasted triangles (and flat bevels + weighted normals already look round).
"""
import bpy, math, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None, flag=False):
    if flag:
        return f"--{name}" in argv
    return argv[argv.index(f"--{name}") + 1] if f"--{name}" in argv else default

WIDTH = float(arg("width", 0.012))
SEGMENTS = int(arg("segments", 2))
ANGLE = math.radians(float(arg("angle", 30)))
LIMIT = 20000

def targets():
    if arg("objects"):
        obs = [bpy.data.objects[n] for n in arg("objects").split(",")]
    elif arg("collection"):
        obs = list(bpy.data.collections[arg("collection")].all_objects)
    elif not bpy.app.background and bpy.context.selected_objects:
        obs = list(bpy.context.selected_objects)
    else:
        obs = list(bpy.context.scene.objects)
    skip = ("guide", "collider", "glass", "decal", "foliage", "leaf")
    return [o for o in obs if o.type == "MESH" and o.data.polygons and not any(s in o.name.lower() for s in skip)]

def finish(ob):
    for m in [m for m in ob.modifiers if m.name in ("MP_Bevel", "MP_WeightedNormal", "MP_Triangulate")]:
        ob.modifiers.remove(m)
    for p in ob.data.polygons:
        p.use_smooth = True
    b = ob.modifiers.new("MP_Bevel", "BEVEL")
    b.width = WIDTH; b.segments = SEGMENTS; b.limit_method = "ANGLE"; b.angle_limit = ANGLE
    b.harden_normals = True; b.use_clamp_overlap = True; b.miter_outer = "MITER_ARC"; b.profile = .5
    w = ob.modifiers.new("MP_WeightedNormal", "WEIGHTED_NORMAL"); w.mode = "FACE_AREA"; w.weight = 50; w.keep_sharp = True
    t = ob.modifiers.new("MP_Triangulate", "TRIANGULATE"); t.keep_custom_normals = True
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    tris = sum(len(p.vertices) - 2 for p in me.polygons); ev.to_mesh_clear()
    if arg("apply", flag=True):
        bpy.context.view_layer.objects.active = ob
        for name in ("MP_Bevel", "MP_WeightedNormal", "MP_Triangulate"):
            bpy.ops.object.modifier_apply(modifier=name)
    return tris

total = 0
for o in targets():
    n = finish(o); total += n
    print(f"{o.name}: {n} tris{'  <-- OVER ROBLOX 20k LIMIT: split or lower segments' if n > LIMIT else ''}", flush=True)
print(f"midpoly: {total} tris total (width {WIDTH} m, {SEGMENTS} seg, {math.degrees(ANGLE):.0f} deg)", flush=True)
if arg("save"):
    bpy.ops.wm.save_as_mainfile(filepath=arg("save"))
