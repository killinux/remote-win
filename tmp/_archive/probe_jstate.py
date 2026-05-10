import bpy
for jn in ("J.胸_後1.L", "J.胸_後2.L", "J.胸_前1.L"):
    j = bpy.data.objects.get(jn)
    if not j: print(f"{jn}: not found"); continue
    rbc = j.rigid_body_constraint
    if not rbc: print(f"{jn}: no rbc"); continue
    print(f"=== {jn} ===")
    print(f"  type={rbc.type} enabled={rbc.enabled}")
    print(f"  o1={rbc.object1.name if rbc.object1 else None} o2={rbc.object2.name if rbc.object2 else None}")
    for ax in ('x','y','z'):
        print(f"  lin_{ax}: use={getattr(rbc,'use_limit_lin_'+ax)} "
              f"lo={getattr(rbc,'limit_lin_'+ax+'_lower'):.4f} hi={getattr(rbc,'limit_lin_'+ax+'_upper'):.4f}")
        print(f"  ang_{ax}: use={getattr(rbc,'use_limit_ang_'+ax)} "
              f"lo={getattr(rbc,'limit_ang_'+ax+'_lower'):.4f} hi={getattr(rbc,'limit_ang_'+ax+'_upper'):.4f}")
