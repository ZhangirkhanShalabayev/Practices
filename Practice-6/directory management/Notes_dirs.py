import os
os.makedirs("test_parent/test_child", exist_ok=True)
print("Directory contents:", os.listdir("."))