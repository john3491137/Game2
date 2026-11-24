"""Build original, low-poly game assets for 小小夢港: 理財夜行者."""
import bpy
import math
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, "..", "models"))
os.makedirs(OUT, exist_ok=True)


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.materials):
        if block.users == 0:
            bpy.data.materials.remove(block)


def material(name, color, roughness=0.85, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


def box(name, loc, size, mat, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Hand-worn edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def sphere(name, loc, scale, mat, parent=None, segments=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=10, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def cylinder(name, loc, radius, depth, mat, parent=None, rotation=None, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc,
                                       rotation=rotation or (0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def empty(name):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    return obj


def export_glb(name):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, name), export_format="GLB",
                              use_selection=True, export_apply=True, export_materials="EXPORT")


def build_hero():
    reset()
    ink = material("Night cloth", (0.075, 0.071, 0.092))
    cloth = material("Plum cloak", (0.20, 0.15, 0.21))
    gold = material("Lantern brass", (0.96, 0.56, 0.16), 0.34, 0.45)
    glass = material("Lantern glass", (1.0, 0.72, 0.30), 0.3)
    root = empty("Dreamer")
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.46, radius2=0.20, depth=1.20,
                                   location=(0, 0, 0.68))
    cloak = bpy.context.object
    cloak.name = "DreamerCloak"
    cloak.data.materials.append(cloth)
    cloak.parent = root
    sphere("Hood", (0, 0, 1.43), (0.30, 0.29, 0.34), ink, root)
    sphere("Face shadow", (0, -0.245, 1.39), (0.15, 0.05, 0.16), ink, root)
    # A tiny brass lamp gives the child a visible, safe navigation cue.
    box("Lantern handle", (0.38, -0.02, 0.91), (0.13, 0.12, 0.36), gold, 0.035, root)
    sphere("Lantern glow", (0.38, -0.03, 0.88), (0.15, 0.13, 0.18), glass, root)
    sphere("Lantern cap", (0.38, -0.03, 1.07), (0.16, 0.14, 0.055), gold, root)
    export_glb("dreamer.glb")


def stage_materials(prefix, cool=False):
    if cool:
        return {
            "wall": material(prefix + " | storm slate", (0.10, 0.16, 0.22)),
            "wall2": material(prefix + " | blue stone", (0.17, 0.24, 0.31)),
            "floor": material(prefix + " | wet planks", (0.20, 0.22, 0.26)),
            "trim": material(prefix + " | iron", (0.28, 0.25, 0.29), 0.42, 0.5),
            "wood": material(prefix + " | dark wood", (0.26, 0.16, 0.13)),
            "gold": material(prefix + " | lantern gold", (0.95, 0.55, 0.16), 0.35, 0.4),
            "hero": material(prefix + " | cloth", (0.12, 0.11, 0.15)),
            "threat": material(prefix + " | distant shadow", (0.055, 0.07, 0.095)),
            "jar1": material(prefix + " | need jar", (0.24, 0.38, 0.38)),
            "jar2": material(prefix + " | savings jar", (0.75, 0.45, 0.16)),
            "jar3": material(prefix + " | want jar", (0.39, 0.27, 0.24)),
        }
    return {
        "wall": material(prefix + " | plum wall", (0.15, 0.12, 0.18)),
        "wall2": material(prefix + " | faded wallpaper", (0.22, 0.17, 0.25)),
        "floor": material(prefix + " | old floorboards", (0.20, 0.17, 0.20)),
        "trim": material(prefix + " | tarnished iron", (0.29, 0.22, 0.27), 0.45, 0.35),
        "wood": material(prefix + " | wine-stained wood", (0.30, 0.19, 0.20)),
        "gold": material(prefix + " | key brass", (0.92, 0.53, 0.15), 0.34, 0.45),
        "hero": material(prefix + " | child silhouette", (0.085, 0.085, 0.11)),
        "threat": material(prefix + " | looming shadow", (0.075, 0.06, 0.08)),
        "jar1": material(prefix + " | needs", (0.38, 0.27, 0.25)),
        "jar2": material(prefix + " | savings", (0.67, 0.40, 0.15)),
        "jar3": material(prefix + " | wants", (0.37, 0.31, 0.23)),
    }


def build_level_one():
    reset()
    m = stage_materials("Fog Ledger Hall")
    box("HallFloor", (0, 0, 0.13), (18, 6, 0.26), m["floor"])
    box("BackWall", (0, 2.8, 4.7), (18, 0.30, 9.4), m["wall"])
    for x in (-8.4, 8.4):
        box("WallPillar", (x, 0.9, 4.55), (0.55, 1.0, 9.0), m["trim"], 0.06)
    for x in (-6.0, -3.0, 0.0, 3.0, 6.0):
        box("FadedWallPanel", (x, 2.56, 5.7), (1.8, 0.12, 2.5), m["wall2"], 0.07)
    # Budget table and the three jars (needs, savings, wants).
    box("LedgerTable", (-1.0, -0.65, 1.45), (3.8, 1.35, 0.26), m["wood"], 0.07)
    for x in (-2.4, 0.4):
        box("TableLeg", (x, -0.45, 0.78), (0.18, 0.22, 1.25), m["wood"], 0.03)
    for x, key in [(-2.0, "jar1"), (-1.0, "jar2"), (0.0, "jar3")]:
        cylinder("BudgetJar", (x, -0.70, 2.04), 0.34, 0.72, m[key], vertices=12)
        cylinder("JarRim", (x, -0.70, 2.42), 0.38, 0.11, m["gold"], vertices=12)
    # Brass lock gate. The slab is found by name and opened only after a correct answer.
    box("GateFrameL", (5.6, 0.5, 2.25), (0.26, 0.5, 4.5), m["trim"], 0.04)
    box("GateFrameR", (7.65, 0.5, 2.25), (0.26, 0.5, 4.5), m["trim"], 0.04)
    box("GateLintel", (6.62, 0.5, 4.42), (2.3, 0.5, 0.28), m["trim"], 0.04)
    box("GateDoor", (6.62, 0.32, 2.20), (1.75, 0.20, 4.1), m["wood"], 0.04)
    # Non-graphic tall shadow in the far background.
    sphere("WatcherHead", (7.3, 1.65, 5.45), (0.48, 0.40, 0.62), m["threat"])
    box("WatcherBody", (7.3, 1.6, 3.65), (0.82, 0.42, 2.2), m["threat"], 0.16)
    # KEY starts hidden; the game reveals it after the budgeting challenge is passed.
    key = empty("KEY")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.23, minor_radius=0.065, major_segments=16,
                                   minor_segments=8, location=(5.20, -0.75, 3.20), rotation=(math.pi/2, 0, 0))
    bpy.context.object.name = "KeyRing"
    bpy.context.object.data.materials.append(m["gold"])
    bpy.context.object.parent = key
    box("KeyShaft", (5.55, -0.75, 3.20), (0.55, 0.10, 0.10), m["gold"], 0.025, key)
    box("KeyTooth", (5.72, -0.75, 3.08), (0.10, 0.10, 0.18), m["gold"], 0.02, key)
    export_glb("fog_ledger_hall.glb")


def build_level_two():
    reset()
    m = stage_materials("Risk Channel", cool=True)
    box("DockFloor", (0, 0, 0.13), (18, 6, 0.26), m["floor"])
    box("StormWall", (0, 2.8, 4.7), (18, 0.30, 9.4), m["wall"])
    for x in (-8.2, 8.2):
        box("DockPillar", (x, 0.9, 4.5), (0.50, 1.0, 8.8), m["trim"], 0.06)
    # Three fictional investment islands visibly differ in stability and risk.
    for x, height, key, top in [(-3.0, 1.3, "jar1", "SteadyIsland"), (-0.4, 2.2, "jar2", "GrowthIsland"), (2.2, 3.1, "jar3", "StormIsland")]:
        box(top, (x, 0.5, 0.35 + height/2), (1.35, 1.05, height), m[key], 0.08)
        sphere(top + "Light", (x, -0.10, 0.55 + height), (0.18, 0.18, 0.18), m["gold"])
    box("EmergencyReserveChest", (-5.4, -0.5, 0.85), (1.45, 1.0, 1.4), m["wood"], 0.06)
    box("BalanceScaleBase", (0.0, -0.8, 0.55), (2.6, 0.45, 0.22), m["trim"], 0.06)
    cylinder("BalanceScalePost", (0.0, -0.8, 1.2), 0.10, 1.2, m["gold"])
    box("BalanceScaleBeam", (0.0, -0.8, 1.85), (2.7, 0.14, 0.16), m["gold"], 0.04)
    # A distant, abstract storm silhouette; no frightening detail or copied character.
    sphere("StormWatcherHead", (7.0, 1.5, 5.1), (0.55, 0.45, 0.66), m["threat"])
    box("StormWatcherBody", (7.0, 1.5, 3.55), (0.95, 0.5, 2.2), m["threat"], 0.20)
    box("GateFrameL", (5.5, 0.5, 2.3), (0.26, 0.5, 4.6), m["trim"], 0.04)
    box("GateFrameR", (7.6, 0.5, 2.3), (0.26, 0.5, 4.6), m["trim"], 0.04)
    box("GateLintel", (6.55, 0.5, 4.5), (2.35, 0.5, 0.28), m["trim"], 0.04)
    box("GateDoor", (6.55, 0.32, 2.25), (1.8, 0.2, 4.2), m["wood"], 0.04)
    key = empty("KEY")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.23, minor_radius=0.065, major_segments=16,
                                   minor_segments=8, location=(5.15, -0.75, 3.2), rotation=(math.pi/2, 0, 0))
    bpy.context.object.name = "KeyRing"
    bpy.context.object.data.materials.append(m["gold"])
    bpy.context.object.parent = key
    box("KeyShaft", (5.5, -0.75, 3.2), (0.55, 0.10, 0.10), m["gold"], 0.025, key)
    box("KeyTooth", (5.67, -0.75, 3.08), (0.10, 0.10, 0.18), m["gold"], 0.02, key)
    export_glb("risk_channel.glb")


build_hero()
build_level_one()
build_level_two()
print("Built Blender assets in", OUT)
