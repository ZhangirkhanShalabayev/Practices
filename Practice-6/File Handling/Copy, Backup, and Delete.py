import shutil
import os
shutil.copy("example.txt", "example_backup.txt")
if os.path.exists("example_backup.txt"):
    os.remove("example_backup.txt")
    print("File deleted.")