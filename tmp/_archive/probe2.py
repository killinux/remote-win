import bpy, json
out = {}
# bust bones
for o in bpy.data.objects:
    if o.type == "ARMATURE" and o.name != ".dummy_armature":
        bust = []
        upper = []
        for b in o.data.bones:
            n = b.name
            if "胸" in n or "乳" in n or "bust" in n.lower() or "breast" in n.lower():
                bust.append({"n": n, "p": b.parent.name if b.parent else None, "head": list(b.head_local), "tail": list(b.tail_local)})
            if "上半身" in n:
                upper.append(n)
        out[o.name] = {"bust": bust, "upper": upper, "total": len(o.data.bones)}

# mmd root children
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            t = o.mmd_type
        except Exception:
            t = "?"
        if t == "ROOT":
            kids = []
            for c in o.children:
                try:
                    cmt = c.mmd_type
                except Exception:
                    cmt = None
                kids.append([c.name, c.type, cmt, len(c.children)])
            out["root_" + o.name] = kids

print("R2BEGIN")
print(json.dumps(out, ensure_ascii=False))
print("R2END")
