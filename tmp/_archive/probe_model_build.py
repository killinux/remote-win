import inspect
from mmd_tools.core.model import Model

src = inspect.getsource(Model.build)
print(src[:8000])
