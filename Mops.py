import pygame
import random
import os
from sprite_manager import load_image

PLAYER_SIZE = 40
RESOURCE_SIZE = 70
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
RED = (255, 0, 0)
GREEN = (0, 255, 0)

mops_type = ['mops']

mops_sprite = None

def get_mops_sprite():
    global mops_sprite
    if mops_sprite is None:
        mops_sprite = load_image("Mops1.png", (PLAYER_SIZE, PLAYER_SIZE))
    return mops_sprite

class Mops:
    def __init__(self, x, y, mops_type, screen):
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = random.choice(['down', 'right', 'up', 'left'])
        self.move_timer = 0
        self.hp = 10
        self.type = mops_type
        self.is_moving = False

    def move(self, resources):
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

        can_move = True
        for res in resources:
            if abs(new_x - res.x) < RESOURCE_SIZE and abs(new_y - res.y) < RESOURCE_SIZE:
                can_move = False
                break

        if can_move:
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, new_x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, new_y))

        self.is_moving = (self.x != prev_x or self.y != prev_y)

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        angle_direction = {'left': 0, 'right': 0, 'up': -90, 'down': 90}
        base_angle = angle_direction.get(self.direction, 0)

        tilt = 0
        if self.is_moving:
            tilt = 10 if (pygame.time.get_ticks() // 100) % 2 == 0 else -10

        total_angle = base_angle + tilt

        sprite = get_mops_sprite()
        if self.direction == 'right':
            sprite = pygame.transform.flip(sprite, True, False)
        if sprite:
            rotated = pygame.transform.rotate(sprite, total_angle)
            rect = rotated.get_rect(center=(draw_x + PLAYER_SIZE // 2, draw_y + PLAYER_SIZE // 2))
            screen.blit(rotated, rect)
        else:
            pygame.draw.rect(screen, GREEN, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))

        # Полоска здоровья
        bar_width = PLAYER_SIZE
        bar_height = 5
        bar_x = draw_x
        bar_y = draw_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.hp / 10) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))

    @staticmethod
    def spawn_mops(existing_objects, mops_types):
        attempts = 100
        for _ in range(attempts):
            x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
            y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
            mops_type = random.choice(mops_types)
            candidate = Mops(x, y, mops_type, None)  # screen не нужен для проверки
            # Проверяем расстояние до существующих объектов
            too_close = False
            for obj in existing_objects:
                dx = candidate.x - obj.x
                dy = candidate.y - obj.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < 140:  # MIN_DISTANCE из gg2
                    too_close = True
                    break
            if not too_close:
                return candidate
        # Если не удалось, спавним в любом случае
        x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
        y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
        mops_type = random.choice(mops_types)
        return Mops(x, y, mops_type, None)