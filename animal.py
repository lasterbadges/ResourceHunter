import pygame
import random
import os

pygame.init()

PLAYER_SIZE = 40
RESOURCE_SIZE = 70
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
RED = (255, 0, 0)
GREEN = (0, 255, 0)
font = pygame.font.SysFont(None, 24)

def load_image(filename, size):
    filepath = os.path.join(os.getcwd(), 'sprites', filename)
    if os.path.exists(filepath):
        try:
            img = pygame.image.load(filepath).convert_alpha()
            if size:
                return pygame.transform.scale(img, size)
            return img
        except pygame.error:
            print(f"Ошибка загрузки {filename}, fallback.")
    return None

animal_types = ['cow', 'wolf', 'sheep']

# Спрайты для животных (по типам)
animal_sprites = {}
directions = ['down', 'right', 'up', 'left']
for animal_type in animal_types:
    animal_sprites[animal_type] = {}
    for dir in directions:
        animal_sprites[animal_type][dir] = {
            'stand': load_image(f"{animal_type}_{dir}_stand.png", (PLAYER_SIZE, PLAYER_SIZE)),
            'walk': [
                load_image(f"{animal_type}_{dir}_walk1.png", (PLAYER_SIZE, PLAYER_SIZE)),
                load_image(f"{animal_type}_{dir}_walk2.png", (PLAYER_SIZE, PLAYER_SIZE)),
                load_image(f"{animal_type}_{dir}_walk3.png", (PLAYER_SIZE, PLAYER_SIZE)),
                load_image(f"{animal_type}_{dir}_walk4.png", (PLAYER_SIZE, PLAYER_SIZE))
            ]
        }

# Fallback для left: flip от right, только если right не None
for animal_type in animal_types:
    for key in ['stand', 'walk']:
        if key == 'stand':
            if animal_sprites[animal_type]['right'][key] is not None:
                animal_sprites[animal_type]['left'][key] = pygame.transform.flip(
                    animal_sprites[animal_type]['right'][key], True, False)
            else:
                animal_sprites[animal_type]['left'][key] = None
        elif key == 'walk':
            animal_sprites[animal_type]['left'][key] = []
            for i in range(4):
                if animal_sprites[animal_type]['right'][key][i] is not None:
                    animal_sprites[animal_type]['left'][key].append(
                        pygame.transform.flip(animal_sprites[animal_type]['right'][key][i], True, False))
                else:
                    animal_sprites[animal_type]['left'][key].append(None)


# Класс Animal (с типом и анимацией)
class Animal:
    def __init__(self, x, y, animal_type):
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = random.choice(['down', 'right', 'up', 'left'])
        self.move_timer = 0
        self.hp = 10  # HP для животных
        self.type = animal_type  # Тип животного
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0

    def move(self, resources):
        prev_x, prev_y = self.x, self.y
        self.move_timer += 1
        if self.move_timer >= 60:  # Сменить направление каждые ~1 сек
            self.direction = random.choice(['down', 'right', 'up', 'left'])
            self.move_timer = 0

        dx, dy = 0, 0
        if self.direction == 'left':
            dx = -self.speed
        elif self.direction == 'right':
            dx = self.speed
        elif self.direction == 'up':
            dy = -self.speed
        elif self.direction == 'down':
            dy = self.speed

        new_x = self.x + dx
        new_y = self.y + dy

        can_move = True
        for res in resources:
            if abs(new_x - res.x) < RESOURCE_SIZE and abs(new_y - res.y) < RESOURCE_SIZE:
                can_move = False
                break

        if can_move:
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, new_x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, new_y))

        self.is_moving = (self.x != prev_x or self.y != prev_y)
        if self.is_moving:
            self.walk_timer += 1
            if self.walk_timer >= 10:
                self.walk_frame = (self.walk_frame + 1) % 4
                self.walk_timer = 0
        else:
            self.walk_frame = 0

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.is_moving:
            sprite = animal_sprites[self.type][self.direction]['walk'][self.walk_frame]
        else:
            sprite = animal_sprites[self.type][self.direction]['stand']

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            color = GREEN if self.type == 'cow' else (128, 128, 128)  # Разные цвета для типов
            pygame.draw.rect(screen, color, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))

        # Полоска здоровья
        bar_width = PLAYER_SIZE
        bar_height = 5
        bar_x = draw_x
        bar_y = draw_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.hp / 10) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))