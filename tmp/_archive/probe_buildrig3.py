import inspect
from mmd_tools.operators import model as model_ops

# Find BuildRig operator
for name, obj in inspect.getmembers(model_ops):
    if 'build' in name.lower() or 'rig' in name.lower():
        print(f"{name}: {obj}")
        if inspect.isclass(obj):
            src = inspect.getsource(obj)
            print(src[:5000])
            print("...")
