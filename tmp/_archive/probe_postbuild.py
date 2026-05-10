import inspect
from mmd_tools.core.model import Model

# Get __postBuild source
src = inspect.getsource(Model._Model__postBuild)
print("=== __postBuild ===")
print(src[:8000])
