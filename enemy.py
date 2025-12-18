import pygame
import random
import os
from sprite_manager import load_image
from sound_manager import sound_manager

ATTACK_RANGE = 50
VISION_RANGE = 200
PLAYER_SIZE = 40
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

enemy_sprite = None


def get_enemy_sprite():
    global enemy_sprite
    if enemy_sprite is None:
        enemy_sprite = load_image("Wolf.png", (PLAYER_SIZE, PLAYER_SIZE))
    return enemy_sprite


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
        self.sound_timer = random.randint(100, 250)  # Таймер для звуков
        self.howl_timer = random.randint(400, 800)  # Отдельный таймер для воя
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0
        self.agro = False
        self.agro_timer = 0

    def move_towards_player(self, player_x, player_y, resources, enemies, player, day_night_cycle=None):
        if day_night_cycle and day_night_cycle.is_day():
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
            self.hp -= 0.01
            if self.hp <= 0:
                pass
            return

        # Обновляем таймеры звуков
        self.sound_timer -= 1
        self.howl_timer -= 1

        # Рандомные звуки волка
        if self.sound_timer <= 0:
            if random.random() < 0.25:  # 25% шанс на звук
                sound_manager.play_npc_sound('wolf', self.x, self.y)
            self.sound_timer = random.randint(150, 350)

        # Вой волка (ночью чаще)
        if not day_night_cycle or not day_night_cycle.is_day():
            if self.howl_timer <= 0 and random.random() < 0.15:
                sound_manager.play_npc_sound('wolf', self.x, self.y)
                self.howl_timer = random.randint(500, 1000)

        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        prev_x, prev_y = self.x, self.y

        if distance <= VISION_RANGE:
            self.agro = True
            self.agro_timer = 300
        elif self.agro:
            self.agro_timer -= 1
            if self.agro_timer <= 0:
                self.agro = False

        if not self.agro:
            self.move_randomly(resources, enemies, player)
            return

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

        if self.x > prev_x:
            self.direction = 'right'
        elif self.x < prev_x:
            self.direction = 'left'
        elif self.y > prev_y:
            self.direction = 'down'
        elif self.y < prev_y:
            self.direction = 'up'

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

    def move_randomly(self, resources, enemies, player):
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

        if self.can_move_to_position(new_x, new_y, resources, enemies, player):
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

    def attack_player(self, player, dt, player_health_bar):
        if not self.agro:
            return
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        if distance <= ATTACK_RANGE and self.attack_timer <= 0:
            player.hp -= self.damage
            player_health_bar.take_damage(self.damage)
            self.attack_timer = 120
            sound_manager.play_random_punch()
        elif self.attack_timer > 0:
            self.attack_timer -= 1

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        angle_direction = {'left': 0, 'right': 0, 'up': -90, 'down': 90}
        base_angle = angle_direction.get(self.direction, 0)

        tilt = 0
        if self.is_moving:
            tilt = 10 if (pygame.time.get_ticks() // 100) % 2 == 0 else -10

        total_angle = base_angle + tilt

        sprite = get_enemy_sprite()
        if self.direction == 'right':
            sprite = pygame.transform.flip(sprite, True, False)
        if sprite:
            rotated = pygame.transform.rotate(sprite, total_angle)
            rect = rotated.get_rect(center=(draw_x + PLAYER_SIZE // 2, draw_y + PLAYER_SIZE // 2))
            screen.blit(rotated, rect)
        else:
            pygame.draw.rect(screen, GREEN, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))

        bar_width = PLAYER_SIZE
        bar_height = 5
        bar_x = draw_x
        bar_y = draw_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.hp / 30) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))