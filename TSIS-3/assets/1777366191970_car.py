import pygame, sys
from pygame.locals import *
import random
import os

pygame.init()

# ===============================================
# ПУТИ И ЗАГРУЗКА ИЗОБРАЖЕНИЙ
# ===============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_image(name):
    """Возвращает полный путь к изображению на основе имени файла"""
    return os.path.join(BASE_DIR, name)

# ===============================================
# КОНФИГУРАЦИЯ ИГРЫ
# ===============================================

# Параметры окна
FPS = 60
clock = pygame.time.Clock()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Границы дороги
ROAD_LEFT = 50
ROAD_RIGHT = 350

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (50, 50, 50)
YELLOW = (255, 255, 0)

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game - Practice 11")

# Шрифты
font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 30)

# ===============================================
# ПАРАМЕТРЫ МОНЕТ С РАЗНЫМИ ВЕСАМИ
# ===============================================
# Словарь с информацией о каждом типе монеты:
# - points: количество очков за сбор
# - weight: вероятность появления (чем выше, тем чаще появляется)
COIN_TYPES = {
    "coin1.png": {"points": 1, "weight": 50, "name": "Bronze", "color": (218, 165, 32)},
    "coin2.png": {"points": 3, "weight": 30, "name": "Silver", "color": (192, 192, 192)},
    "coin3.png": {"points": 5, "weight": 20, "name": "Gold", "color": (255, 215, 0)}
}

# Параметры сложности
SPEED_INCREASE_INTERVAL = 5  # Увеличивать скорость врага каждые N монет
BASE_ENEMY_SPEED = 10

# Переменные состояния игры
coin_count = 0
total_points = 0
road_offset = 0
game_over = False
current_enemy_speed = BASE_ENEMY_SPEED

# ===============================================
# ФУНКЦИЯ ОТРИСОВКИ ДОРОГИ
# ===============================================
def draw_road(surface, offset):
    """
    Отрисовывает дорогу с границами и разметкой
    
    Args:
        surface: поверхность для отрисовки
        offset: смещение для анимации разметки
    """
    # Заливаем фон дороги серым цветом
    surface.fill(GRAY)

    # Отрисовываем белые границы дороги (левая и правая)
    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, SCREEN_HEIGHT), 5)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 5)

    # Отрисовываем жёлтую разметку по центру дороги с анимацией
    for y in range(-40, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, YELLOW,
                         (200, y + offset),
                         (200, y + 20 + offset), 5)

# ===============================================
# КЛАСС ИГРОВЫХ ОБЪЕКТОВ
# ===============================================
class GameObject:
    """
    Базовый класс для всех движущихся объектов в игре:
    игрока, врага, монет
    """
    def __init__(self, image_path, size, x, y, speed=0, controllable=False):
        """
        Инициализация игрового объекта
        
        Args:
            image_path: путь к изображению объекта
            size: кортеж (ширина, высота) для масштабирования
            x, y: начальные координаты центра объекта
            speed: скорость движения вниз (0 для неподвижных)
            controllable: управляется ли объект игроком
        """
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.controllable = controllable

    def update(self):
        """Обновляет состояние объекта (движение, управление)"""
        # Обработка управления игроком (стрелки влево/вправо)
        if self.controllable:
            keys = pygame.key.get_pressed()

            # Движение влево с проверкой границ дороги
            if keys[K_LEFT] and self.rect.left > ROAD_LEFT:
                self.rect.x -= 5

            # Движение вправо с проверкой границ дороги
            if keys[K_RIGHT] and self.rect.right < ROAD_RIGHT:
                self.rect.x += 5

        # Движение вниз для врагов и монет
        if self.speed:
            self.rect.y += self.speed

            # Если объект вышел за нижний край экрана, перезагрузить его
            if self.rect.top > SCREEN_HEIGHT:
                self.reset()

    def reset(self):
        """
        Перезагружает объект в верхней части экрана
        со случайной позицией по горизонтали в пределах дороги
        """
        self.rect.center = (
            random.randint(ROAD_LEFT + self.rect.width // 2,
                           ROAD_RIGHT - self.rect.width // 2),
            -50
        )

    def draw(self, surface):
        """Отрисовывает объект на заданной поверхности"""
        surface.blit(self.image, self.rect)

# ===============================================
# КЛАСС МОНЕТЫ С РАЗНЫМИ ТИПАМИ
# ===============================================
class Coin(GameObject):
    """
    Специализированный класс для монет,
    поддерживающий разные типы с разными стоимостями
    """
    def __init__(self, x, y, speed=5):
        """
        Инициализация монеты со случайным типом
        
        Args:
            x, y: начальные координаты
            speed: скорость движения вниз
        """
        # Выбираем случайный тип монеты на основе весов
        self.coin_type = self._random_coin_type()
        coin_info = COIN_TYPES[self.coin_type]
        
        # Инициализируем как GameObject с выбранным типом монеты
        super().__init__(
            load_image(self.coin_type),
            (30, 30),
            x, y,
            speed=speed
        )
        
        # Сохраняем очки этой конкретной монеты
        self.points = coin_info["points"]
        self.name = coin_info["name"]

    def _random_coin_type(self):
        """
        Выбирает случайный тип монеты на основе весов вероятности
        
        Returns:
            строка с именем файла монеты
        """
        # Собираем список всех монет и их весов
        coin_list = list(COIN_TYPES.keys())
        weights = [COIN_TYPES[coin]["weight"] for coin in coin_list]
        
        # Используем random.choices для взвешенного случайного выбора
        return random.choices(coin_list, weights=weights, k=1)[0]

# ===============================================
# ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ И ПЕРЕЗАГРУЗКИ ИГРЫ
# ===============================================
def reset_game():
    """
    Инициализирует или перезагружает все игровые объекты
    и сбрасывает переменные состояния
    """
    global player, enemy, coin, coin_count, total_points, road_offset, game_over, current_enemy_speed

    # Создаём игрока (управляемый объект в нижней части экрана)
    player = GameObject(
        load_image("player.png"),
        (60, 120),
        200,  # центральная позиция по горизонтали
        520,  # нижняя часть экрана
        controllable=True
    )

    # Создаём врага (неуправляемый объект, движется вниз)
    enemy = GameObject(
        load_image("enemy.png"),
        (58, 116),
        200,
        0,
        speed=BASE_ENEMY_SPEED
    )

    # Создаём первую монету со случайным типом
    coin = Coin(200, -50, speed=5)

    # Сбрасываем счётчики
    coin_count = 0
    total_points = 0
    road_offset = 0
    current_enemy_speed = BASE_ENEMY_SPEED
    game_over = False

# Инициализируем игру при запуске
reset_game()

# ===============================================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# ===============================================
while True:
    # Обработка событий
    for event in pygame.event.get():
        # Выход из игры при закрытии окна
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Перезагрузка игры при нажатии F на экране "Game Over"
        if game_over and event.type == KEYDOWN:
            if event.key == K_f:
                reset_game()

    # Обновление состояния игры только если игра не окончена
    if not game_over:
        # Обновляем позиции всех объектов
        player.update()
        enemy.update()
        coin.update()

        # Обновляем анимацию дорожной разметки
        road_offset += 5
        if road_offset >= 40:
            road_offset = 0

        # ===============================================
        # ЛОГИКА СБОРА МОНЕТ
        # ===============================================
        if player.rect.colliderect(coin.rect):
            # Получаем информацию о собранной монете
            coin_count += 1
            points_earned = coin.points
            total_points += points_earned
            
            # Отладочный вывод в консоль (опционально)
            print(f"Собрана монета: {coin.name} ({points_earned} очков) | Всего: {total_points}")
            
            # Создаём новую монету со случайным типом
            coin.coin_type = coin._random_coin_type()
            coin_info = COIN_TYPES[coin.coin_type]
            coin.image = pygame.image.load(load_image(coin.coin_type)).convert_alpha()
            coin.image = pygame.transform.scale(coin.image, (30, 30))
            coin.points = coin_info["points"]
            coin.name = coin_info["name"]
            coin.reset()
            
            # ===============================================
            # УВЕЛИЧЕНИЕ СЛОЖНОСТИ: СКОРОСТЬ ВРАГА
            # ===============================================
            # Каждые N монет увеличиваем скорость врага на 2 пиксела в секунду
            if coin_count % SPEED_INCREASE_INTERVAL == 0:
                current_enemy_speed += 2
                enemy.speed = current_enemy_speed
                print(f"СЛОЖНОСТЬ ВОЗРОСЛА! Скорость врага: {current_enemy_speed}")

        # ===============================================
        # ОБНАРУЖЕНИЕ СТОЛКНОВЕНИЯ С ВРАГОМ
        # ===============================================
        if player.rect.colliderect(enemy.rect):
            game_over = True

    # ===============================================
    # ОТРИСОВКА ИГРЫ
    # ===============================================
    
    # Отрисовываем дорогу
    draw_road(screen, road_offset)

    # Отрисовываем игровые объекты (порядок важен для наслоения)
    player.draw(screen)
    coin.draw(screen)   # Монета отрисовывается первой
    enemy.draw(screen)  # Враг отрисовывается сверху

    # ===============================================
    # ОТРИСОВКА ИНТЕРФЕЙСА
    # ===============================================
    
    # Показываем количество собранных монет
    text = font.render(f"Coins: {coin_count}", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH - 130, 10))

    # Показываем общие очки
    points_text = font.render(f"Points: {total_points}", True, BLACK)
    screen.blit(points_text, (10, 10))

    # Показываем текущую скорость врага
    speed_text = font.render(f"Speed: {current_enemy_speed}", True, BLACK)
    screen.blit(speed_text, (SCREEN_WIDTH - 130, 40))

    # ===============================================
    # ЭКРАН "GAME OVER"
    # ===============================================
    if game_over:
        # Отрисовываем текст "GAME OVER"
        over_text = big_font.render("GAME OVER", True, BLACK)
        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, 80))

        # Отрисовываем финальную статистику
        final_coins = font.render(f"Final Coins: {coin_count}", True, BLACK)
        screen.blit(final_coins, (SCREEN_WIDTH//2 - final_coins.get_width()//2, 140))

        final_points = font.render(f"Final Points: {total_points}", True, BLACK)
        screen.blit(final_points, (SCREEN_WIDTH//2 - final_points.get_width()//2, 170))

        final_speed = font.render(f"Enemy Speed: {current_enemy_speed}", True, BLACK)
        screen.blit(final_speed, (SCREEN_WIDTH//2 - final_speed.get_width()//2, 200))

        # Создаём кнопку перезагрузки
        button_width = 220
        button_height = 50
        button_x = SCREEN_WIDTH//2 - button_width//2 
        button_y = SCREEN_HEIGHT//2 + 50

        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Отрисовываем кнопку (белое заполнение, чёрная граница)
        pygame.draw.rect(screen, WHITE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 3)

        # Отрисовываем текст на кнопке
        btn_text = font.render("Press F to restart", True, BLACK)
        screen.blit(
            btn_text,
            (
                button_rect.centerx - btn_text.get_width()//2,
                button_rect.centery - btn_text.get_height()//2
            )
        )

    # Обновляем дисплей
    pygame.display.update()
    clock.tick(FPS)
