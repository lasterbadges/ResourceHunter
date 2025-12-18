import pygame
import random
import os
from sprite_manager import load_image
from sound_manager import sound_manager  # Импортируем менеджер звуков

# Constants
ATTACK_RANGE = 50  # Радиус атаки для врагов
VISION_RANGE = 200  # Радиус, в котором враг замечает игрока
PLAYER_SIZE = 40
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
RED = (255, 0, 0)  # Для врагов
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Загрузка спрайтов для врагов
enemy_sprites = {}
directions = ['down', 'right', 'up', 'left']
for dir in directions:
    enemy_sprites[dir] = {
        'stand': load_image(f"enemy_{dir}_stand.png", (PLAYER_SIZE, PLAYER_SIZE)),
        'walk': [
            load_image(f"enemy_{dir}_walk1.png", (PLAYER_SIZE, PLAYER_SIZE)),
            load_image(f"enemy_{dir}_walk2.png", (PLAYER_SIZE, PLAYER_SIZE)),
            load_image(f"enemy_{dir}_walk3.png", (PLAYER_SIZE, PLAYER_SIZE)),
            load_image(f"enemy_{dir}_walk4.png", (PLAYER_SIZE, PLAYER_SIZE))
        ]
    }

# Fallback для left: flip от right, только если right не None
for key in ['stand', 'walk']:
    if key == 'stand':
        if enemy_sprites['right'][key] is not None:
            enemy_sprites['left'][key] = pygame.transform.flip(enemy_sprites['right'][key], True, False)
        else:
            enemy_sprites['left'][key] = None
    elif key == 'walk':
        enemy_sprites['left'][key] = []
        for i in range(4):
            if enemy_sprites['right'][key][i] is not None:
                enemy_sprites['left'][key].append(
                    pygame.transform.flip(enemy_sprites['right'][key][i], True, False))
            else:
                enemy_sprites['left'][key].append(None)




class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.hp = 30
        self.damage = 6
        self.attack_timer = 0
        self.direction = random.choice(['down', 'right', 'up', 'left'])
        self.move_timer = 0
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0
        self.agro = False  # Флаг АГРО (преследования)
        self.agro_timer = 0  # Таймер потери АГРО (в кадрах)

    def can_move_to_position(self, new_x, new_y, resources, enemies, player):
        if (new_x < 0 or new_x > WORLD_WIDTH - PLAYER_SIZE or
                new_y < 0 or new_y > WORLD_HEIGHT - PLAYER_SIZE):
            self.hp = 0
        if (abs(new_x - player.x) < PLAYER_SIZE and
                abs(new_y - player.y) < PLAYER_SIZE):
            return False
        for enemy in enemies:
            if enemy != self:
                if (abs(new_x - enemy.x) < PLAYER_SIZE - 15 and
                        abs(new_y - enemy.y) < PLAYER_SIZE - 15):
                    return False
        return True

    def move_towards_player(self, player_x, player_y, resources, enemies, player, day_night_cycle=None):
        if day_night_cycle and day_night_cycle.is_day():
            # Убегать от игрока днем
            distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
            if distance > 0:
                dx = (self.x - player_x) / distance * (self.speed + 2)
                dy = (self.y - player_y) / distance * (self.speed + 2)
                new_x = self.x + dx
                new_y = self.y + dy
                if self.can_move_to_position(new_x, new_y, resources, enemies, player):
                    self.x = new_x
                    self.y = new_y
                    self.is_moving = True
                    # Определить направление
                    if dx > 0:
                        self.direction = 'right'
                    elif dx < 0:
                        self.direction = 'left'
                    elif dy > 0:
                        self.direction = 'down'
                    elif dy < 0:
                        self.direction = 'up'
                else:
                    self.is_moving = False
            self.hp -= 0.01  # Постепенная смерть днем
            if self.hp <= 0:
                pass  # Удаление в main
            return

        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        prev_x, prev_y = self.x, self.y

        # Проверка на активацию/потерю АГРО
        if distance <= VISION_RANGE:
            self.agro = True
            self.agro_timer = 300  # Сброс таймера (~5 сек при 60 FPS)
        elif self.agro:
            self.agro_timer -= 1
            if self.agro_timer <= 0:
                self.agro = False

        if not self.agro:
            # Случайное движение, как у Animal (когда АГРО потеряна)
            self.move_randomly(resources, enemies, player)
            return

        # Преследование, если АГРО активно
        if distance <= ATTACK_RANGE:
            self.is_moving = False
            self.walk_frame = 0
            return

        dx = max(-self.speed, min(self.speed, player_x - self.x))
        dy = max(-self.speed, min(self.speed, player_y - self.y))
        new_x = self.x + dx
        new_y = self.y + dy

        if self.can_move_to_position(new_x, new_y, resources, enemies, player):
            self.x = new_x
            self.y = new_y
            self.is_moving = True
        else:
            self.is_moving = False

        if self.is_moving:
            self.walk_timer += 1
            if self.walk_timer >= 10:
                self.walk_frame = (self.walk_frame + 1) % 4
                self.walk_timer = 0
        else:
            self.walk_frame = 0

        # Определение направления на основе движения
        if self.x > prev_x:
            self.direction = 'right'
        elif self.x < prev_x:
            self.direction = 'left'
        elif self.y > prev_y:
            self.direction = 'down'
        elif self.y < prev_y:
            self.direction = 'up'

    def move_randomly(self, resources, enemies, player):
        # Случайное блуждание (аналогично Animal.move, но без взаимодействия с ресурсами для простоты)
        prev_x, prev_y = self.x, self.y
        self.move_timer += 1
        if self.move_timer >= 60:  # Смена направления ~1 раз в сек
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

        if self.can_move_to_position(new_x, new_y, resources, enemies, player):
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, new_x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, new_y))

        self.is_moving = (self.x != prev_x or self.y != prev_y)
        if self.is_moving:
            self.walk_timer += 1
            if self.walk_timer >= 10:  # Скорость анимации
                self.walk_frame = (self.walk_frame + 1) % 4
                self.walk_timer = 0
        else:
            self.walk_frame = 0

    def attack_player(self, player, dt, player_health_bar):
        if not self.agro:
            return  # Не атакуем, если нет АГРО
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        if distance <= ATTACK_RANGE and self.attack_timer <= 0:
            player.hp -= self.damage  # Предполагаем player.hp; замените на player.health если нужно
            player_health_bar.take_damage(self.damage)
            self.attack_timer = 120
            # Воспроизводим звук удара
            sound_manager.play_random_punch()
        elif self.attack_timer > 0:
            self.attack_timer -= 1

    def draw(self, screen, camera_x, camera_y):
        # Спрайты для врагов
        enemy_sprites = {}
        directions = ['down', 'right', 'up', 'left']
        for dir in directions:
            enemy_sprites[dir] = {
                'stand': load_image(f"enemy_{dir}_stand.png", (PLAYER_SIZE, PLAYER_SIZE)),
                'walk': [
                    load_image(f"enemy_{dir}_walk1.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"enemy_{dir}_walk2.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"enemy_{dir}_walk3.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"enemy_{dir}_walk4.png", (PLAYER_SIZE, PLAYER_SIZE))
                ]
            }

        # Fallback для left: flip от right, только если right не None
        for key in ['stand', 'walk']:
            if key == 'stand':
                if enemy_sprites['right'][key] is not None:
                    enemy_sprites['left'][key] = pygame.transform.flip(enemy_sprites['right'][key], True, False)
                else:
                    enemy_sprites['left'][key] = None
            elif key == 'walk':
                enemy_sprites['left'][key] = []
                for i in range(4):
                    if enemy_sprites['right'][key][i] is not None:
                        enemy_sprites['left'][key].append(
                            pygame.transform.flip(enemy_sprites['right'][key][i], True, False))
                    else:
                        enemy_sprites['left'][key].append(None)

        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.is_moving:
            sprite = enemy_sprites[self.direction]['walk'][self.walk_frame]
        else:
            sprite = enemy_sprites[self.direction]['stand']

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))

        # Полоска здоровья
        bar_width = PLAYER_SIZE
        bar_height = 5
        bar_x = draw_x
        bar_y = draw_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.hp / 30) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))