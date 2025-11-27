import pygame
import random
import os
import math

# Constants
BOSS_SIZE = 80
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
PLAYER_SIZE = 40
RESOURCE_SIZE = 70
BOSS_ATTACK_RANGE = 80  # Радиус атаки для босса
BOSS_VISION_RANGE = 300  # Радиус нацеливания для босса
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Функции загрузки изображений
def load_image(filename, size):
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        try:
            img = pygame.image.load(filepath).convert_alpha()
            if size:
                return pygame.transform.scale(img, size)
            return img
        except pygame.error:
            print(f"Ошибка загрузки {filename}, fallback.")
    return None

# Спрайты для босса
boss_sprites = {}
directions = ['down', 'right', 'up', 'left']
for dir in directions:
    boss_sprites[dir] = {
        'stand': load_image(f"boss_{dir}_stand.png", (BOSS_SIZE, BOSS_SIZE)),
        'walk': [
            load_image(f"boss_{dir}_walk1.png", (BOSS_SIZE, BOSS_SIZE)),
            load_image(f"boss_{dir}_walk2.png", (BOSS_SIZE, BOSS_SIZE)),
            load_image(f"boss_{dir}_walk3.png", (BOSS_SIZE, BOSS_SIZE)),
            load_image(f"boss_{dir}_walk4.png", (BOSS_SIZE, BOSS_SIZE))
        ]
    }

# Fallback для left: flip от right, только если right не None
for key in ['stand', 'walk']:
    if key == 'stand':
        if boss_sprites['right'][key] is not None:
            boss_sprites['left'][key] = pygame.transform.flip(boss_sprites['right'][key], True, False)
        else:
            boss_sprites['left'][key] = None
    elif key == 'walk':
        boss_sprites['left'][key] = []
        for i in range(4):
            if boss_sprites['right'][key][i] is not None:
                boss_sprites['left'][key].append(pygame.transform.flip(boss_sprites['right'][key][i], True, False))
            else:
                boss_sprites['left'][key].append(None)


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BOSS_SIZE
        self.speed = 1.5
        self.hp = 500
        self.damage = 10
        self.push_damage = 0  # Отталкивание не убирает HP, но толкает
        self.attack_timer = 0
        self.push_timer = 0
        self.ranged_timer = 0
        self.aiming = False
        self.aim_start_time = 0
        self.direction = random.choice(['down', 'right', 'up', 'left'])
        self.move_timer = 0
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0
        self.agro = False
        self.agro_timer = 0
        self.attack_range = BOSS_ATTACK_RANGE
        self.vision_range = BOSS_VISION_RANGE

    def can_move_to_position(self, new_x, new_y, resources, enemies, player, bosses):
        if (new_x < 0 or new_x > WORLD_WIDTH - self.size or
                new_y < 0 or new_y > WORLD_HEIGHT - self.size):
            return False
        if (abs(new_x - player.x) < self.size and
                abs(new_y - player.y) < self.size):
            return False
        for enemy in enemies:
            if (abs(new_x - enemy.x) < self.size and
                    abs(new_y - enemy.y) < self.size):
                return False
        for boss in bosses:
            if boss != self:
                if (abs(new_x - boss.x) < self.size and
                        abs(new_y - boss.y) < self.size):
                    return False
        for res in resources:
            if abs(new_x - res.x) < RESOURCE_SIZE and abs(new_y - res.y) < RESOURCE_SIZE:
                return False
        return True

    def move_towards_player(self, player_x, player_y, resources, enemies, player, bosses):
        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        prev_x, prev_y = self.x, self.y

        # Проверка на активацию/потерю АГРО
        if distance <= self.vision_range:
            self.agro = True
            self.agro_timer = 300  # Сброс таймера (~5 сек при 60 FPS)
        elif self.agro:
            self.agro_timer -= 1
            if self.agro_timer <= 0:
                self.agro = False

        if not self.agro:
            # Случайное движение
            self.move_randomly(resources, enemies, player, bosses)
            return

        # Преследование
        if distance <= self.attack_range:
            self.is_moving = False
            self.walk_frame = 0
            return

        dx = max(-self.speed, min(self.speed, player_x - self.x))
        dy = max(-self.speed, min(self.speed, player_y - self.y))
        new_x = self.x + dx
        new_y = self.y + dy

        if self.can_move_to_position(new_x, new_y, resources, enemies, player, bosses):
            self.x = int(new_x)
            self.y = int(new_y)
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

        # Определение направления
        if self.x > prev_x:
            self.direction = 'right'
        elif self.x < prev_x:
            self.direction = 'left'
        elif self.y > prev_y:
            self.direction = 'down'
        elif self.y < prev_y:
            self.direction = 'up'

    def move_randomly(self, resources, enemies, player, bosses):
        prev_x, prev_y = self.x, self.y
        self.move_timer += 1
        if self.move_timer >= 60:
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

        if self.can_move_to_position(new_x, new_y, resources, enemies, player, bosses):
            self.x = max(0, min(WORLD_WIDTH - self.size, int(new_x)))
            self.y = max(0, min(WORLD_HEIGHT - self.size, int(new_y)))

        self.is_moving = (self.x != prev_x or self.y != prev_y)
        if self.is_moving:
            self.walk_timer += 1
            if self.walk_timer >= 10:
                self.walk_frame = (self.walk_frame + 1) % 4
                self.walk_timer = 0
        else:
            self.walk_frame = 0

    def attack_player(self, player, dt, fireballs):
        if not self.agro:
            return
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5

        # Базовая атака вблизи
        if distance <= self.attack_range and self.attack_timer <= 0:
            player.hp -= self.damage
            self.attack_timer = 120  # 2 сек cooldown
        elif self.attack_timer > 0:
            self.attack_timer -= 1

        # Отталкивание
        if distance <= self.attack_range + 20 and self.push_timer <= 0:
            # Толкаем игрока назад с кувырком
            dx = player.x - self.x
            dy = player.y - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > 0:
                player.dirx = dx / dist
                player.diry = dy / dist
                # Установить направление для анимации
                if abs(player.dirx) > abs(player.diry):
                    player.direction = 'right' if player.dirx > 0 else 'left'
                else:
                    player.direction = 'down' if player.diry > 0 else 'up'
                player.is_rolling = True
                player.roll_timer = 0
                player.roll_frame = 0
                player.roll_duration = 0
            self.push_timer = 300  # 5 сек cooldown

        elif self.push_timer > 0:
            self.push_timer -= 1

        # Дальняя атака
        if distance > self.attack_range and distance <= self.vision_range and self.ranged_timer <= 0:
            self.aiming = True
            self.aim_start_time = pygame.time.get_ticks()
            self.ranged_timer = 600  # 10 сек cooldown
        elif self.aiming:
            current_time = pygame.time.get_ticks()
            if current_time - self.aim_start_time >= 1500:  # 1.5 сек
                # Выпустить fireball
                fireball = Fireball(self.x + self.size // 2, self.y + self.size // 2, player.x + PLAYER_SIZE // 2,
                                    player.y + PLAYER_SIZE // 2)
                fireballs.append(fireball)
                self.aiming = False
        elif self.ranged_timer > 0:
            self.ranged_timer -= 1

    def draw(self, screen, camera_x, camera_y, player):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.is_moving:
            sprite = boss_sprites[self.direction]['walk'][self.walk_frame]
        else:
            sprite = boss_sprites[self.direction]['stand']

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, (255, 0, 255), (draw_x, draw_y, self.size, self.size))  # Пурпурный для босса

        # Полоска здоровья
        bar_width = self.size
        bar_height = 5
        bar_x = draw_x
        bar_y = draw_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.hp / 500) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))

        # Полоска прицеливания
        if self.aiming:
            pygame.draw.line(screen, (255, 255, 0), (draw_x + self.size // 2, draw_y + self.size // 2),
                             (player.x - camera_x + PLAYER_SIZE // 2, player.y - camera_y + PLAYER_SIZE // 2), 3)


class Fireball:
    def __init__(self, x, y, target_x, target_y, speed=8):
        self.x = x
        self.y = y
        dx = target_x - x
        dy = target_y - y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 0:
            self.dx = dx / dist * speed
            self.dy = dy / dist * speed
        else:
            self.dx = 0
            self.dy = 0
        self.size = 20
        self.lifetime = 300  # 5 секунд при 60 FPS
        self.timer = 0

    def move(self):
        self.x = int(self.x + self.dx)
        self.y = int(self.y + self.dy)
        self.timer += 1

    def is_expired(self):
        return self.timer > self.lifetime

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        pygame.draw.circle(screen, (255, 100, 0), (int(draw_x + self.size // 2), int(draw_y + self.size // 2)),
                           self.size // 2)