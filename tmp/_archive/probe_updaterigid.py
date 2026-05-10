import inspect
from mmd_tools.core.model import Model

src = inspect.getsource(Model.updateRigid)
print(src[:8000])
