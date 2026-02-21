import math

def degree_to_radian(degree):
    return degree * (math.pi / 180)

def trapezoid_area(height, base1, base2):
    return ((base1 + base2) / 2) * height

def regular_polygon_area(sides, length):
    return (sides * length**2) / (4 * math.tan(math.pi / sides))

def parallelogram_area(base, height):
    return float(base * height)

if name == "main":
    # 1. Градусы в радианы
    deg = 15
    print(f"Input degree: {deg}")
    print(f"Output radian: {degree_to_radian(deg):.6f}")

    print("-" * 20)

    # 2. Площадь трапеции
    h_trap = 5
    b1 = 5
    b2 = 6
    print(f"Height: {h_trap}")
    print(f"Base, first value: {b1}")
    print(f"Base, second value: {b2}")
    print(f"Expected Output: {trapezoid_area(h_trap, b1, b2)}")

    print("-" * 20)

    # 3. Площадь правильного многоугольника
    n_sides = 4
    side_len = 25
    print(f"Input number of sides: {n_sides}")
    print(f"Input the length of a side: {side_len}")
    print(f"The area of the polygon is: {regular_polygon_area(n_sides, side_len):.0f}")

    print("-" * 20)

    # 4. Площадь параллелограмма
    p_base = 5
    p_height = 6
    print(f"Length of base: {p_base}")
    print(f"Height of parallelogram: {p_height}")
    print(f"Expected Output: {parallelogram_area(p_base, p_height)}")