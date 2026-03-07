with open("example.txt", "w") as f:
    f.write("Hello, this is the first line.\n")
with open("example.txt", "a") as f:
    f.write("This is an appended line.\n")
with open("example.txt", "r") as f:
    content = f.read()
    print("File Content:\n", content)