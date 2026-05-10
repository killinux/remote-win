import inspect, mmd_tools.core.model as M
src = inspect.getsource(M.Model.createRigidBody)
print("=== createRigidBody ===")
print(src)
print("=== createJoint ===")
src2 = inspect.getsource(M.Model.createJoint)
print(src2)
