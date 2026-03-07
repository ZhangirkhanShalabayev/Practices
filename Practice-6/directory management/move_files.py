import shutil
import os

# Task: Move/copy files between directories
if not os.path.exists("test_parent"):
    os.mkdir("test_parent")

with open("temp.txt", "w") as f: f.write("moving...")
shutil.move("temp.txt", "test_parent/moved_temp.txt")