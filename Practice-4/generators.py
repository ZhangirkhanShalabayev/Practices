def squares_up_to(n):
    for i in range(n + 1):
        yield i  2

def even_generator(n):
    for i in range(0, n + 1, 2):
        yield i

def divisible_by_3_and_4(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

def squares(a, b):
    for i in range(a, b + 1):
        yield i  2

def countdown(n):
    while n >= 0:
        yield n
        n -= 1

if name == "main":
    # Проверка квадратов до N
    print(list(squares_up_to(5)))

    # Проверка четных чисел через консоль
    n_input = int(input("Введите n: "))
    print(", ".join(str(x) for x in even_generator(n_input)))

    # Проверка делимости на 3 и 4
    print(list(divisible_by_3_and_4(50)))

    # Проверка квадратов от a до b
    for val in squares(3, 7):
        print(val)

    # Проверка обратного отсчета
    for num in countdown(5):
        print(num)