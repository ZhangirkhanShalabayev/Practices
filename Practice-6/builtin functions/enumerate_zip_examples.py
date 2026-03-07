chars = ['a', 'b', 'c']
vals = [10, 20, 30]

# zip
for char, val in zip(chars, vals):
    print(f"Pair: {char}-{val}")

# enumerate
for i, char in enumerate(chars):
    print(f"Index {i}: {char}")