import bpy

# Toggle visibility of all rigid body objects
visible = None
for o in bpy.data.objects:
    if o.rigid_body or (hasattr(o, 'mmd_type') and o.mmd_type in ('RIGID_BODY', 'JOINT_GRP_OBJ', 'RIGID_GRP_OBJ')):
        if visible is None:
            visible = o.hide_viewport
        o.hide_viewport = not visible
        o.hide_set(not visible)

# Also toggle the rigidbodies/joints group empties
for o in bpy.data.objects:
    if o.name in ('rigidbodies', 'joints') or 'rigid' in o.name.lower():
        if o.type == 'EMPTY':
            o.hide_viewport = not visible

state = "VISIBLE" if visible else "HIDDEN"
print(f"Rigid bodies: {state}")
