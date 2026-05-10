import inspect
from mmd_tools.core.model import Model

src = inspect.getsource(Model.buildRigids)
print(src[:8000])
print("\n\n=== buildJoints ===")
src2 = inspect.getsource(Model.buildJoints)
print(src2[:4000])
