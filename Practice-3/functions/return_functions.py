def my_function(x, y):
  return x + y

result = my_function(5, 3)
print(result)

#A function that returns a list:
def my_function():
  return ["apple", "banana", "cherry"]
fruits = my_function()
print(fruits[0])
print(fruits[1])
print(fruits[2])

#A function that returns a tuple:
def my_function():
  return (10, 20)

x, y = my_function()
print("x:", x)
print("y:", y)

def my_function(name, /):
  print("Hello", name)
my_function("Emil")