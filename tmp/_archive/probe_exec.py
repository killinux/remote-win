import inspect, mmd_tools.core.pmx.exporter as exp_mod
# get the private class via name mangling
PmxExporter = getattr(exp_mod, '_exporter__PmxExporter', None)
if PmxExporter is None:
    # Try name mangling lookup directly
    for n in dir(exp_mod):
        if 'PmxExporter' in n:
            print('found:', n)
            PmxExporter = getattr(exp_mod, n)
            break
if PmxExporter is None:
    # access via vars
    for n, v in vars(exp_mod).items():
        if inspect.isclass(v) and 'PmxExporter' in n:
            PmxExporter = v
            print('via vars:', n)
            break
print("class:", PmxExporter)
if PmxExporter:
    sig = inspect.signature(PmxExporter.execute)
    print("execute sig:", sig)
    src = inspect.getsource(PmxExporter.execute)
    print(src[:2000])
