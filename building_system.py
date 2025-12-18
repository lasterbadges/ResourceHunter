import pygame

screen_width = 800
screen_height = 800
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
PLAYER_SIZE = 40
RESOURCE_SIZE = 70
FONT_SIZE = 24
MENU_WIDTH = 400
MENU_HEIGHT = 300
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
MIN_DISTANCE = RESOURCE_SIZE * 2  # Минимальное расстояние между ресурсами (100 пикселей)
TILE_SIZE = 128  # Размер тайла травы
ATTACK_RANGE = 50  # Радиус атаки для врагов
VISION_RANGE = 200  # Радиус, в котором враг замечает игрока
BOSS_ATTACK_RANGE = 80  # Радиус атаки для босса
BOSS_VISION_RANGE = 300  # Радиус нацеливания для босса
BOSS_SIZE = 80
PUSHBACK_RANGE = 120  # Радиус атаки отталкивания
PUSHBACK_DAMAGE = 5  # Урон от отталкивания
PUSHBACK_FORCE = 15  # Сила отталкивания
PUSHBACK_COOLDOWN = 15000  # Перезарядка отталкивания (15 секунд)


BUILDING_SIZE = 60  # Размер построек

# Colors
GRASS_GREEN = (34, 139, 34)  # Зеленый для травы (fallback)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
LIGHT_GRAY = (200, 200, 200)
SEMI_BLACK = (0, 0, 0, 128)  # Полупрозрачный для фона меню
RED = (255, 0, 0)  # Для врагов
ORANGE = (255, 165, 0)  # Для костра
BLUE = (0, 0, 255)  # Для верстака
YELLOW = (255, 255, 0)  # Для палатки
DARK_RED = (139, 0, 0)  # Для капкана
FLESH = (255, 218, 185)  # Телесный цвет для обводки палатки

class Building:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_  # 'workbench', 'tent', 'trap', 'campfire'
        self.size = BUILDING_SIZE

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        if 0 <= draw_x <= screen_width and 0 <= draw_y <= screen_height:
            if self.type == 'workbench':
                # Столешница
                pygame.draw.rect(screen, BROWN, (draw_x, draw_y + 20, self.size, 10))
                # Левая ножка
                pygame.draw.rect(screen, BROWN, (draw_x + 5, draw_y + 30, 5, 30))
                # Правая ножка
                pygame.draw.rect(screen, BROWN, (draw_x + self.size - 10, draw_y + 30, 5, 30))
            elif self.type == 'tent':
                # Треугольная палатка с обводкой по бокам и полоской
                pygame.draw.polygon(screen, YELLOW, [(draw_x, draw_y + self.size), (draw_x + self.size // 2, draw_y),
                                                     (draw_x + self.size, draw_y + self.size)])
                # Боковые линии толще
                pygame.draw.line(screen, FLESH, (draw_x + self.size // 2, draw_y), (draw_x, draw_y + self.size), 5)
                pygame.draw.line(screen, FLESH, (draw_x + self.size // 2, draw_y), (draw_x + self.size, draw_y + self.size), 5)
                # Полоска по середине
                pygame.draw.line(screen, FLESH, (draw_x + self.size // 2, draw_y), (draw_x + self.size // 2, draw_y + self.size), 3)
            elif self.type == 'trap':
                pygame.draw.rect(screen, DARK_RED, (draw_x + 10, draw_y + 30, 40, 10))
                pygame.draw.circle(screen, GRAY, (draw_x + 30, draw_y + 35), 15, 2)
            elif self.type == 'campfire':
                pygame.draw.circle(screen, GRAY, (draw_x + 30, draw_y + 30), 25)
                pygame.draw.circle(screen, ORANGE, (draw_x + 30, draw_y + 30), 15)
                # Мерцание можно добавить в update, но здесь просто круг