import pygame
import random

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game - No Reverse")

black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
gray = (40, 40, 40)

cell_size = 20
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 25)
big_font = pygame.font.SysFont("arial", 40)

def draw_grid():
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, gray, (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, gray, (0, y), (width, y))


def show_stats(score, level):
    text = font.render(f"Score: {score}  Level: {level}", True, white)
    screen.blit(text, (10, 10))


def generate_food(snake):
    while True:
        x = random.randrange(0, width, cell_size)
        y = random.randrange(0, height, cell_size)
        if [x, y] not in snake:
            return x, y


def game_loop():

    game_over = False
    game_close = False

    x = width // 2
    y = height // 2

    x_speed = 0
    y_speed = 0

    direction = "STOP"  

    snake = []
    length = 1

    score = 0
    level = 1
    speed = 8

    foodx, foody = generate_food(snake)

    while not game_over:

        while game_close:
            screen.fill(black)

            msg1 = big_font.render("GAME OVER", True, red)
            msg2 = font.render("C - Restart | Q - Quit", True, white)

            screen.blit(msg1, (width//2 - 120, height//2 - 50))
            screen.blit(msg2, (width//2 - 140, height//2 + 10))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:

                # запрет разворота на 180°
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    x_speed = -cell_size
                    y_speed = 0
                    direction = "LEFT"

                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    x_speed = cell_size
                    y_speed = 0
                    direction = "RIGHT"

                elif event.key == pygame.K_UP and direction != "DOWN":
                    y_speed = -cell_size
                    x_speed = 0
                    direction = "UP"

                elif event.key == pygame.K_DOWN and direction != "UP":
                    y_speed = cell_size
                    x_speed = 0
                    direction = "DOWN"


        if x < 0 or x >= width or y < 0 or y >= height:
            game_close = True


        x += x_speed
        y += y_speed

        screen.fill(black)
        draw_grid()

        snake_head = [x, y]
        snake.append(snake_head)

        if len(snake) > length:
            del snake[0]

        for segment in snake[:-1]:
            if segment == snake_head:
                game_close = True

        for segment in snake:
            pygame.draw.rect(screen, green, [segment[0], segment[1], cell_size, cell_size])

        pygame.draw.rect(screen, red, [foodx, foody, cell_size, cell_size])

        if x == foodx and y == foody:
            foodx, foody = generate_food(snake)
            length += 1
            score += 1

            if score % 3 == 0:
                level += 1
                speed += 2

        show_stats(score, level)

        pygame.display.update()
        clock.tick(speed)

    pygame.quit()
    quit()


game_loop()