import bpy
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
print(f"arm={arm.name}")
for bn in ("boob right 1", "boob left 1", "boob right 2", "boob left 2", "上半身2"):
    b = arm.data.bones.get(bn)
    if not b: print(f"{bn}: missing"); continue
    h = arm.matrix_world @ b.head_local
    t = arm.matrix_world @ b.tail_local
    print(f"{bn}: head=({h.x:.3f},{h.y:.3f},{h.z:.3f}) tail=({t.x:.3f},{t.y:.3f},{t.z:.3f}) length={(t-h).length:.3f}")
    direction = (t - h).normalized()
    print(f"  direction: ({direction.x:.3f},{direction.y:.3f},{direction.z:.3f})")
