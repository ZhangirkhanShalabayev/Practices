import pygame
import sys
import datetime

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

import os

base_path = os.path.dirname(__file__)

def load_image(name):
    return pygame.image.load(os.path.join(base_path, "images", name))

clock_image = load_image("clock.png")
min_hand_image = load_image("min_hand.png")
sec_hand_image = load_image("sec_hand.png")

clock_rect = clock_image.get_rect(center=(300, 300))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    current_time = datetime.datetime.now()
    minute = current_time.minute
    second = current_time.second

    min_angle = -(minute * 6)
    sec_angle = -(second * 6)

    rotated_min_hand = pygame.transform.rotate(min_hand_image, min_angle)
    rotated_sec_hand = pygame.transform.rotate(sec_hand_image, sec_angle)

    min_hand_rect = rotated_min_hand.get_rect(center=clock_rect.center)
    sec_hand_rect = rotated_sec_hand.get_rect(center=clock_rect.center)

    screen.fill((255, 255, 255))
    screen.blit(clock_image, clock_rect)
    screen.blit(rotated_min_hand, min_hand_rect)
    screen.blit(rotated_sec_hand, sec_hand_rect)

    pygame.display.flip()
    clock.tick(30)