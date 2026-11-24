import bpy, math, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = r"C:\Windows\Fonts\msjhbd.ttc"

def rgb(h):
    h=h.lstrip("#")
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

def mat(name, color, rough=0.82, metallic=0, noise=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=rgb(color)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=rgb(color)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metallic
    if noise:
        n=m.node_tree.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value=5.5
        n.inputs["Detail"].default_value=3
        bump=m.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=noise
        bump.inputs["Distance"].default_value=0.12
        m.node_tree.links.new(n.outputs["Fac"],bump.inputs["Height"])
        m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m

def cube(name, loc, scale, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b=o.modifiers.new("Soft silhouette","BEVEL")
        b.width=bevel
        b.segments=2
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    if material: o.data.materials.append(material)
    return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material: o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cylinder(name, loc, radius, depth, material, rot=None, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot or (0,0,0))
    o=bpy.context.object
    o.name=name
    if material:o.data.materials.append(material)
    b=o.modifiers.new("Soft edge","BEVEL")
    b.width=0.04
    b.segments=2
    o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

def text(body, loc, size, material, font, align="LEFT"):
    c=bpy.data.curves.new("Traditional Chinese UI","FONT")
    c.body=body
    c.size=size
    c.align_x=align
    c.extrude=0.001
    if font:c.font=font
    o=bpy.data.objects.new(body,c)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(math.radians(90),0,0)
    o.data.materials.append(material)
    return o

def light(name, typ, loc, energy, color, size=5):
    d=bpy.data.lights.new(name,typ)
    d.energy=energy
    d.color=rgb(color)[:3]
    if typ=="AREA": d.shape="DISK"; d.size=size
    o=bpy.data.objects.new(name,d)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(math.radians(35),0,math.radians(25))
    return o

def make_variant(v, font):
    clear()
    mats={k:mat(k,c,v["rough"],0,v["noise"]) for k,c in v["colors"].items()}
    wall=mats["wall"]; dark=mats["dark"]; floor=mats["floor"]; gold=mats["gold"]
    # Same 2.5D corridor and puzzle state in all three directions.
    cube("Back wall",(0,1.7,4.5),(16,0.5,9),wall,0)
    cube("Floor",(0,0.2,0.05),(16,6,0.22),floor,0.025)
    for i in range(13):
        x=-7.3+i*1.22
        cube("Floor seam",(x,-0.85,0.18),(0.035,3.6,0.012),dark,0)
    for x in (-7.15,7.15):
        cube("Gothic wall rib",(x,0.6,4.45),(0.48,1.0,8.7),mats["trim"],0.06)
    for x in (-5.6,-2.8,0,2.8,5.6):
        cube("Wall panel",(x,1.40,5.45),(1.6,0.08,2.7),mats["wall2"],0.06)
    # Door and open passage on the right.
    cube("Door frame left",(4.1,0.62,2.25),(0.26,0.55,4.4),mats["trim"],0.06)
    cube("Door frame right",(6.25,0.62,2.25),(0.26,0.55,4.4),mats["trim"],0.06)
    cube("Door lintel",(5.18,0.62,4.35),(2.3,0.55,0.28),mats["trim"],0.06)
    door=cube("Opened door",(4.30,0.30,2.0),(1.75,0.18,3.85),mats["door"],0.05)
    door.rotation_euler[2]=math.radians(-22)
    cube("Dark passage",(5.18,1.35,2.3),(1.72,0.12,4.0),dark,0)
    # Puzzle altar and three budget jars: need 30, saving 10, want 10.
    cube("Puzzle table",(0.35,-0.55,1.52),(3.2,1.5,0.24),mats["wood"],0.08)
    for x in (-0.82,1.52):
        cube("Table leg",(x,-0.46,0.83),(0.20,0.25,1.3),mats["wood"],0.04)
    for x,key,col in [(-0.52,"NEED","jar1"),(0.35,"SAVE","jar2"),(1.22,"WANT","jar3")]:
        cylinder("Budget jar",(x,-0.56,2.15),0.34,0.68,mats[col])
        cylinder("Jar rim",(x,-0.56,2.51),0.37,0.11,gold)
        for j in range(3 if key!="SAVE" else 1):
            cylinder("NT coin",(x+(j-1)*0.12,-0.78,2.04+j*0.055),0.085,0.035,gold)
    # Small player and looming shadow creature.
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.48, radius2=0.20, depth=1.25, location=(-3.25,-0.20,1.35))
    cloak=bpy.context.object; cloak.name="Lantern child cloak"; cloak.data.materials.append(mats["hero"])
    sphere("Hooded head",(-3.25,-0.28,2.12),(0.27,0.26,0.31),mats["hero"])
    sphere("Lantern glow",(-2.86,-0.40,1.26),(0.11,0.11,0.15),gold)
    # Figure in far right: threat is atmospheric and non-graphic.
    sphere("Tall shadow head",(6.15,0.55,5.10),(0.53,0.40,0.68),mats["threat"])
    cube("Tall shadow body",(6.15,0.54,3.60),(0.92,0.48,2.4),mats["threat"],0.23)
    for s in (-1,1):
        arm=cube("Long shadow arm",(6.15+s*0.77,0.53,3.42),(0.26,0.30,1.95),mats["threat"],0.10)
        arm.rotation_euler[1]=math.radians(-10*s)
    sphere("Tiny eyes",(6.15,0.07,5.12),(0.26,0.055,0.07),gold)
    # KEY floats in front of the open lock.
    bpy.ops.mesh.primitive_torus_add(major_radius=0.19,minor_radius=0.055,major_segments=24,minor_segments=8,location=(3.55,-1.35,3.25),rotation=(math.radians(90),0,0))
    keyring=bpy.context.object; keyring.name="KEY ring"; keyring.data.materials.append(gold)
    cube("KEY shaft",(3.87,-1.35,3.25),(0.54,0.10,0.09),gold,0.035)
    cube("KEY tooth",(4.04,-1.35,3.14),(0.09,0.10,0.18),gold,0.02)
    # HUD overlay, identical content and position for all directions.
    ui=mats["ui"]; ink=mats["ink"]; accent=mats["accent"]
    cube("Top HUD",(0,-3.3,8.38),(15.4,0.12,0.78),ui,0.10)
    text("夢港夜行者",(-7.25,-3.40,8.27),0.36,accent,font)
    text("第 1 關｜霧市帳本",(-3.55,-3.40,8.27),0.31,ink,font)
    text("關卡分數  320", (4.80,-3.40,8.27),0.31,accent,font)
    cube("Challenge card",(2.15,-3.2,6.72),(8.5,0.12,1.52),ui,0.10)
    text("小挑戰：50 元中先支付 30 元必要花費",(-1.82,-3.31,7.14),0.30,ink,font)
    text("分配結果：需要 30｜儲蓄 10｜想要 10",(-1.82,-3.31,6.68),0.28,ink,font)
    # Consequence/result and primary action.
    cube("Result card",(-1.20,-3.15,0.48),(9.9,0.12,0.82),ui,0.10)
    text("答對！存下 10 元 → 門鎖亮起　+100 分",(-5.82,-3.27,0.64),0.31,accent,font)
    text("按 E 拿取 KEY，前往第 2 關",(-5.82,-3.27,0.31),0.27,ink,font)
    # World label attached to the puzzle.
    text("需要",(-0.78,-1.45,2.72),0.18,ink,font)
    text("儲蓄", (0.12,-1.45,2.72),0.18,accent,font)
    text("想要", (1.00,-1.45,2.72),0.18,ink,font)
    # Lighting and camera.
    light("Moon key","AREA",(-5,-7,9),1150,v["keylight"],7)
    light("Lantern fill","AREA",(1,-5,4),450,v["fill"],4)
    light("Threat rim","AREA",(7,1,7),800,v["rim"],3)
    world=bpy.data.worlds.new("Dream harbor night") if not bpy.data.worlds else bpy.data.worlds[0]
    bpy.context.scene.world=world
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=rgb(v["world"])
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.35
    cam_data=bpy.data.cameras.new("Mockup camera")
    cam=bpy.data.objects.new("Mockup camera",cam_data); bpy.context.collection.objects.link(cam)
    cam.location=(0,-20,5.0)
    target=Vector((0,0,4.35))
    cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO"; cam.data.ortho_scale=16.6
    bpy.context.scene.camera=cam
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.color_type="MATERIAL"; scene.display.shading.light=v["lighting"]; scene.display.shading.show_shadows=v["shadows"]; scene.display.shading.show_cavity=v["cavity"]; scene.display.shading.cavity_type="BOTH"; scene.display.shading.show_object_outline=v["outline"]
    scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.view_settings.view_transform="Standard"
    scene.view_settings.look="Medium High Contrast"
    scene.display.shading.light="STUDIO"
    scene.render.film_transparent=False
    scene.camera.data.lens=50
    scene.render.filepath=os.path.join(OUT,v["file"])
    bpy.ops.render.render(write_still=True)

try:
    font=bpy.data.fonts.load(FONT_PATH)
except Exception as e:
    print("CJK font could not be loaded:",e)
    font=None

variants=[
 {"file":"01-gothic-puppet.png","rough":0.9,"noise":0.32,"world":"#111019","keylight":"#d7a96c","fill":"#837188","rim":"#786b96","lighting":"STUDIO","shadows":True,"cavity":True,"outline":False,
  "colors":{"wall":"#312c39","wall2":"#3c3345","floor":"#403742","dark":"#17151f","trim":"#59475a","door":"#211c29","wood":"#52404a","gold":"#e6ad58","hero":"#282531","threat":"#211923","jar1":"#8a655d","jar2":"#d49a48","jar3":"#867257","ui":"#191821","ink":"#fff6e8","accent":"#ffd78c"}},
 {"file":"02-cut-paper-fable.png","rough":1.0,"noise":0.0,"world":"#13202a","keylight":"#f2cb73","fill":"#86a5a5","rim":"#647b8c","lighting":"FLAT","shadows":False,"cavity":False,"outline":True,
  "colors":{"wall":"#34424b","wall2":"#42545e","floor":"#56636a","dark":"#1c2931","trim":"#60727a","door":"#23333b","wood":"#79624d","gold":"#ffd36f","hero":"#26343b","threat":"#34434a","jar1":"#8aa9a2","jar2":"#f0c76b","jar3":"#cc8e68","ui":"#fff4dc","ink":"#101c24","accent":"#3f2a16"}},
 {"file":"03-dream-diorama.png","rough":0.48,"noise":0.04,"world":"#101d2e","keylight":"#ffc96b","fill":"#71a9bf","rim":"#6d98c5","lighting":"STUDIO","shadows":True,"cavity":True,"outline":False,
  "colors":{"wall":"#23344a","wall2":"#30465e","floor":"#38495d","dark":"#101b2b","trim":"#536a7a","door":"#1c2d43","wood":"#725943","gold":"#ffd166","hero":"#25364a","threat":"#223148","jar1":"#5f8b9a","jar2":"#f4c35d","jar3":"#ba8160","ui":"#142338","ink":"#f4f7f6","accent":"#ffd166"}}
]
for v in variants:
    make_variant(v,font)
print("Rendered three visual directions to",OUT)




