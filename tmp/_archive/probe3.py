import bpy, json
out = {}
arm = bpy.data.objects.get("Inase54_arm")
if arm:
    # plausible bust-equivalents in xps converts
    cand = []
    for b in arm.data.bones:
        n = b.name
        ln = n.lower()
        if any(k in ln for k in ("bust","breast","chest","oppai","tit","boob","bre")):
            cand.append([n, b.parent.name if b.parent else None])
    out["candidates"] = cand
    # bones whose head Z is between Z of 上半身2 and 上半身3 (rough chest area), and Y < 0 (forward) — heuristic
    ub2 = arm.data.bones.get("上半身2")
    ub3 = arm.data.bones.get("上半身3")
    if ub2 and ub3:
        z_lo, z_hi = sorted([ub2.head_local.z, ub3.head_local.z])
        chest_area = []
        for b in arm.data.bones:
            h = b.head_local
            if z_lo <= h.z <= z_hi + 0.1 and h.y < -0.02 and abs(h.x) < 0.3:
                if b.parent and "上半身" in b.parent.name:
                    chest_area.append([b.name, b.parent.name, list(h)])
        out["chest_area_heuristic"] = chest_area[:30]

# mmd_tools API surface
try:
    import mmd_tools
    out["mmd_tools_path"] = getattr(mmd_tools, "__file__", "?")
    try:
        from mmd_tools.core.model import Model
        out["Model_methods"] = sorted([m for m in dir(Model) if not m.startswith("_")])
    except Exception as e:
        out["Model_err"] = str(e)
except Exception as e:
    out["mmd_tools_err"] = str(e)

# also confirm rigidbodies/joints group via mmd_tools API
try:
    from mmd_tools.core.model import Model
    root = bpy.data.objects.get("Inase54")
    if root:
        m = Model(root)
        rg = m.rigidGroupObject()
        jg = m.jointGroupObject()
        out["model_rigid_grp"] = rg.name if rg else None
        out["model_joint_grp"] = jg.name if jg else None
        out["rigid_count_after"] = len(rg.children) if rg else None
except Exception as e:
    out["model_call_err"] = str(e)

print("R3BEGIN"); print(json.dumps(out, ensure_ascii=False)); print("R3END")
