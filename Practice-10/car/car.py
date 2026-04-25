import pygame, sys
from pygame.locals import *
import random
import os

pygame.init()

# ------------------- ПУТИ -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_image(name):
    return os.path.join(BASE_DIR, name)

# ------------------- НАСТРОЙКИ -------------------
FPS = 60
clock = pygame.time.Clock()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

ROAD_LEFT = 50
ROAD_RIGHT = 350

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (50, 50, 50)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game")

font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 30)

coin_count = 0
road_offset = 0
game_over = False

# ------------------- ДОРОГА -------------------
def draw_road(surface, offset):
    surface.fill(GRAY)

    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, SCREEN_HEIGHT), 5)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 5)

    for y in range(-40, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, YELLOW,
                         (200, y + offset),
                         (200, y + 20 + offset), 5)

# ------------------- ОБЪЕКТ -------------------
class GameObject:
    def __init__(self, image_path, size, x, y, speed=0, controllable=False):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.controllable = controllable

    def update(self):
        if self.controllable:
            keys = pygame.key.get_pressed()

            if keys[K_LEFT] and self.rect.left > ROAD_LEFT:
                self.rect.x -= 5

            if keys[K_RIGHT] and self.rect.right < ROAD_RIGHT:
                self.rect.x += 5

        if self.speed:
            self.rect.y += self.speed

            if self.rect.top > SCREEN_HEIGHT:
                self.reset()

    def reset(self):
        self.rect.center = (
            random.randint(ROAD_LEFT + self.rect.width // 2,
                           ROAD_RIGHT - self.rect.width // 2),
            -50
        )

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ------------------- RESET -------------------
def reset_game():
    global player, enemy, coin, coin_count, road_offset, game_over

    player = GameObject(load_image("player.png"), (60, 120), 200, 520, controllable=True)
    enemy = GameObject(load_image("enemy.png"), (58, 116), 200, 0, speed=10)
    coin = GameObject(load_image("coin1.png"), (30, 30), 200, -50, speed=5)

    coin_count = 0
    road_offset = 0
    game_over = False

reset_game()

# ------------------- GAME LOOP -------------------
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if game_over and event.type == KEYDOWN:
            if event.key == K_f:
                reset_game()

    if not game_over:
        player.update()
        enemy.update()
        coin.update()

        road_offset += 5
        if road_offset >= 40:
            road_offset = 0

        if player.rect.colliderect(coin.rect):
            coin_count += 1
            coin.reset()

        if player.rect.colliderect(enemy.rect):
            game_over = True

    # ------------------- DRAW -------------------
    draw_road(screen, road_offset)

    player.draw(screen)
    coin.draw(screen)   # сначала монета
    enemy.draw(screen)  # потом враг (он сверху)

    text = font.render(f"Coins: {coin_count}", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH - 130, 10))

    # ------------------- GAME OVER -------------------
    if game_over:
        over_text = big_font.render("GAME OVER", True, BLACK)
        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, 120))

        button_width = 220
        button_height = 50

        button_x = SCREEN_WIDTH//2 - button_width//2 
        button_y = SCREEN_HEIGHT//2

        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        pygame.draw.rect(screen, WHITE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 3)

        btn_text = font.render("Press F to restart", True, BLACK)
        screen.blit(
            btn_text,
            (
                button_rect.centerx - btn_text.get_width()//2,
                button_rect.centery - btn_text.get_height()//2
            )
        )

    pygame.display.update()
    clock.tick(FPS)