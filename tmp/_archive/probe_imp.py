import importlib, pkgutil, mmd_tools.core.pmx as pmx_pkg
print("PKG:", pmx_pkg.__file__)
print("DIR:", [n for n in dir(pmx_pkg) if not n.startswith("_")])
# walk submodules
for m in pkgutil.iter_modules(pmx_pkg.__path__):
    print("submod:", m.name)
# try importer signature
from mmd_tools.core.pmx.importer import PMXImporter
import inspect
sig = inspect.signature(PMXImporter.execute)
print("PMXImporter.execute sig:", sig)
src = inspect.getsource(PMXImporter.execute)
print("PMXImporter.execute first 1500 chars:")
print(src[:1500])
