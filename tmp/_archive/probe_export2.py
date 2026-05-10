import inspect, mmd_tools.core.pmx.exporter as exp_mod
print("export sig:", inspect.signature(exp_mod.export))
print(inspect.getsource(exp_mod.export)[:800])
