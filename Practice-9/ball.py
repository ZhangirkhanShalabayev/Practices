import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

ball_radius = 25
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
step = 20

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if ball_y - step >= ball_radius:
                    ball_y -= step
            elif event.key == pygame.K_DOWN:
                if ball_y + step <= HEIGHT - ball_radius:
                    ball_y += step
            elif event.key == pygame.K_LEFT:
                if ball_x - step >= ball_radius:
                    ball_x -= step
            elif event.key == pygame.K_RIGHT:
                if ball_x + step <= WIDTH - ball_radius:
                    ball_x += step

    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)
    
    pygame.display.flip()
    clock.tick(60)