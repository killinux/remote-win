import os
d = r"E:\mywork\mymodel\yaoxiang"
print("DIR_EXISTS:", os.path.isdir(d))
if os.path.isdir(d):
    for f in os.listdir(d):
        fp = os.path.join(d, f)
        print(f"  {f}  ({os.path.getsize(fp)} bytes)")
