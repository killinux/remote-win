import bpy, math, os
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.model import Model

# Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)

# Import both models
models = {
    "Inase54_Simple": r"E:\mywork\mymodel\inase54_simple_phys.pmx",
    "Target": r"E:\mywork\mymodel\Purifier Inase 18\Purifier Inase 18 V1.pmx",
}

results = {}
for label, path in models.items():
    if not os.path.isfile(path):
        print(f"SKIP {label}: file not found")
        continue

    # Clean before each import
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)

    PMXImporter().execute(filepath=path,
        types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
        scale=1.0, clean_model=False, remove_doubles=False)
    root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
    arm = next((c for c in root.children if c.type=="ARMATURE"), None)
    model = Model(root)

    data = {"label": label, "rigids": [], "joints": [], "bust_bones": []}

    for rb in model.rigidBodies():
        mmd = rb.mmd_rigid
        blender_rb = rb.rigid_body
        info = {
            "name": rb.name,
            "bone": mmd.bone,
            "type": mmd.type,
            "shape": mmd.shape,
            "size": tuple(round(x,3) for x in mmd.size),
            "mass": round(blender_rb.mass, 3) if blender_rb else 0,
            "friction": round(blender_rb.friction, 3) if blender_rb else 0,
            "restitution": round(blender_rb.restitution, 3) if blender_rb else 0,
            "lin_damp": round(blender_rb.linear_damping, 3) if blender_rb else 0,
            "ang_damp": round(blender_rb.angular_damping, 3) if blender_rb else 0,
            "group": mmd.collision_group_number,
            "kinematic": blender_rb.kinematic if blender_rb else None,
        }
        data["rigids"].append(info)

    for j in model.joints():
        mj = j.mmd_joint
        rbc = j.rigid_body_constraint
        info = {
            "name": j.name,
            "obj1": rbc.object1.name if rbc and rbc.object1 else "?",
            "obj2": rbc.object2.name if rbc and rbc.object2 else "?",
            "type": rbc.type if rbc else "?",
            "lin_lo": tuple(round(getattr(rbc, f"limit_lin_{ax}_lower", 0), 4) for ax in "xyz") if rbc else None,
            "lin_hi": tuple(round(getattr(rbc, f"limit_lin_{ax}_upper", 0), 4) for ax in "xyz") if rbc else None,
            "ang_lo": tuple(round(math.degrees(getattr(rbc, f"limit_ang_{ax}_lower", 0)), 1) for ax in "xyz") if rbc else None,
            "ang_hi": tuple(round(math.degrees(getattr(rbc, f"limit_ang_{ax}_upper", 0)), 1) for ax in "xyz") if rbc else None,
            "spring_lin": tuple(round(x, 1) for x in mj.spring_linear),
            "spring_ang": tuple(round(x, 1) for x in mj.spring_angular),
        }
        data["joints"].append(info)

    # Bust bones
    for b in arm.data.bones:
        bl = b.name.lower()
        if any(kw in bl for kw in ("bust","breast","boob","胸","乳","oppai")):
            data["bust_bones"].append({"name": b.name, "parent": b.parent.name if b.parent else None})

    results[label] = data

# Print comparison
for label, data in results.items():
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    print(f"\n  Bust bones: {[b['name'] for b in data['bust_bones']]}")

    # Only show bust-related rigids
    print(f"\n  --- Bust Rigid Bodies ---")
    for rb in data["rigids"]:
        bone = rb["bone"].lower()
        if any(kw in bone for kw in ("bust","breast","boob","胸","乳","oppai","上半身")):
            print(f"  {rb['name']}:")
            print(f"    bone={rb['bone']} type={rb['type']} shape={rb['shape']}")
            print(f"    mass={rb['mass']} friction={rb['friction']} restitution={rb['restitution']}")
            print(f"    damping=({rb['lin_damp']}, {rb['ang_damp']}) size={rb['size']}")
            print(f"    group={rb['group']} kinematic={rb['kinematic']}")

    print(f"\n  --- Bust Joints ---")
    for j in data["joints"]:
        name = j["name"].lower()
        if any(kw in name for kw in ("胸","乳","bust","boob","breast")):
            print(f"  {j['name']}: {j['obj1']} -> {j['obj2']}")
            print(f"    type={j['type']}")
            print(f"    lin: {j['lin_lo']} ~ {j['lin_hi']}")
            print(f"    ang: {j['ang_lo']} ~ {j['ang_hi']}")
            print(f"    spring_lin={j['spring_lin']} spring_ang={j['spring_ang']}")

# Side by side diff
if len(results) == 2:
    labels = list(results.keys())
    print(f"\n{'='*60}")
    print(f"  DIFF: {labels[0]} vs {labels[1]}")
    print(f"{'='*60}")

    for key in ("rigids", "joints"):
        items0 = [x for x in results[labels[0]][key] if any(kw in x["name"].lower() for kw in ("胸","乳","bust","boob"))]
        items1 = [x for x in results[labels[1]][key] if any(kw in x["name"].lower() for kw in ("胸","乳","bust","boob"))]
        print(f"\n  {key}: {labels[0]} has {len(items0)}, {labels[1]} has {len(items1)}")

        if items0 and items1:
            i0 = items0[0]
            i1 = items1[0]
            for k in i0:
                v0 = i0[k]
                v1 = i1.get(k)
                if v0 != v1:
                    print(f"    {k}: {v0} vs {v1}")
