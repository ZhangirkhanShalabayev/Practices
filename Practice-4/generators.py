import re

def get_business_pattern():
    pattern_string = r"^(Book|Mattress|Grocery) (store|supplier)$"
    return re.compile(pattern_string)


pattern = get_business_pattern()
print(bool(pattern.search("Book store")))
print(bool(pattern.search("Mattress supplier")))
print(bool(pattern.search("Book shop")))
print(bool(pattern.search("The Book store")