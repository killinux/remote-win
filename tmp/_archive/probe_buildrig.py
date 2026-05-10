import inspect
from mmd_tools.core import model as model_mod

# Find the build method in Model class
src = inspect.getsource(model_mod.Model.buildRig)
print(src[:6000])
