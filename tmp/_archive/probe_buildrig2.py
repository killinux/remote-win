import inspect, mmd_tools

# Find build_rig operator
from mmd_tools.operators import rigid_body as rb_ops
src = inspect.getsource(rb_ops)
# Find the build_rig class
print(src[:8000])
