import pygame
from sprite_manager import load_image
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
tree_img = load_image("tree.png", (RESOURCE_SIZE, RESOURCE_SIZE))
rock_img = load_image("stone.png", (RESOURCE_SIZE, RESOURCE_SIZE))


class Resource:
    def __init__(self, x, y, type_):
        self.rock_img = rock_img
        self.tree_img = tree_img
        self.x = x
        self.y = y
        self.type = type_  # 'tree' or 'rock'
        self.hp = 10

    def take_damage(self, tool):
        damage = 1
        if self.type == 'tree' and tool == 'axe':
            damage = 3
        elif self.type == 'rock' and tool == 'pickaxe':
            damage = 3
        self.hp -= damage
        return self.hp <= 0

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        if 0 <= draw_x <= screen_width and 0 <= draw_y <= screen_height:
            img = self.tree_img if self.type == 'tree' else self.rock_img
            if img:
                screen.blit(img, (draw_x, draw_y))
            else:
                color = BROWN if self.type == 'tree' else GRAY
                pygame.draw.rect(screen, color, (draw_x, draw_y, RESOURCE_SIZE, RESOURCE_SIZE))