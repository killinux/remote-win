import inspect, mmd_tools.core.model as M
src = inspect.getsource(M)
# Find where mmd_tools_rigid_parent is referenced
import re
for m in re.finditer(r"mmd_tools_rigid_parent", src):
    start = max(0, m.start() - 200)
    end = min(len(src), m.end() + 300)
    print("---ctx---")
    print(src[start:end])
print("=== buildRigids ===")
print(inspect.getsource(M.Model.buildRigids))
