import pygame
import math
from animal import Animal
from enemy import Enemy
from sprite_manager import load_image
from sound_manager import sound_manager  # Импортируем менеджер звуков

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


player_sprites = {}
directions = ['down', 'right', 'up', 'left']





class PushbackWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = PUSHBACK_RANGE
        self.alpha = 200
        self.lifetime = 20  # Фреймов
        self.timer = 0

    def update(self):
        self.timer += 1
        # Расширяем круг
        self.radius = int(10 + (self.max_radius - 10) * (self.timer / self.lifetime))
        # Уменьшаем прозрачность
        self.alpha = int(200 * (1 - self.timer / self.lifetime))

    def is_expired(self):
        return self.timer >= self.lifetime

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        if self.alpha > 0:
            # Создаём поверхность для круга с прозрачностью
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 165, 0, self.alpha), (self.radius, self.radius), self.radius, 3)
            screen.blit(surface, (draw_x - self.radius, draw_y - self.radius))


class Lightning:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.frame = 0
        self.timer = 0
        self.lifetime = 30  # 0.5 сек

    def update(self):
        self.timer += 1
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % 3

    def is_expired(self):
        return self.timer > self.lifetime

    def draw(self, screen, camera_x, camera_y):
        # Загрузка текстурки молнии
        lightning_img = load_image("lightning.png", None)
        # Позиция в середине линии
        mid_x = (self.x1 + self.x2) / 2
        mid_y = (self.y1 + self.y2) / 2
        if lightning_img:
            # Поворот текстурки: начало (низ) к игроку, конец (верх) к цели
            dx = self.x2 - self.x1
            dy = self.y2 - self.y1
            angle = math.degrees(math.atan2(dy, dx))
            rotated_img = pygame.transform.rotate(lightning_img, angle)
            rect = rotated_img.get_rect(center=(mid_x - camera_x, mid_y - camera_y))
            screen.blit(rotated_img, rect)
        else:
            pygame.draw.rect(screen, (255, 255, 0), (mid_x - camera_x, mid_y - camera_y, 15, 50))


class Player:
    def __init__(self, screen):
        for dir in directions:
            player_sprites[dir] = {
                'stand': load_image(f"player_{dir}_stand.png", (PLAYER_SIZE, PLAYER_SIZE)),
                'walk': [
                    load_image(f"player_{dir}_walk1.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"player_{dir}_walk2.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"player_{dir}_walk3.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"player_{dir}_walk4.png", (PLAYER_SIZE, PLAYER_SIZE))
                ],
                'roll': [
                    load_image(f"player_{dir}_roll1.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"player_{dir}_roll2.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"player_{dir}_roll3.png", (PLAYER_SIZE, PLAYER_SIZE)),
                    load_image(f"player_{dir}_roll4.png", (PLAYER_SIZE, PLAYER_SIZE))
                ]
            }
        for key in ['stand', 'walk', 'roll']:
            if isinstance(player_sprites['right'][key], list):
                for i in range(len(player_sprites['right'][key])):
                    if player_sprites['right'][key][i] is not None and not player_sprites['left'][key][i]:
                        player_sprites['left'][key][i] = pygame.transform.flip(player_sprites['right'][key][i], True,
                                                                               False)
            else:
                if player_sprites['right'][key] is not None and not player_sprites['left'][key]:
                    player_sprites['left'][key] = pygame.transform.flip(player_sprites['right'][key], True, False)
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        self.speed = 5
        self.dirx = 0
        self.diry = 0
        self.hp = 100
        self.mana = 100  # Текущая мана
        self.max_mana = 100  # Максимальная мана
        self.mana_regen_rate = 10 / 60000  # 10 маны в минуту (в миллисекундах)
        self.hunger_timer = 0  # Таймер голода
        self.direction = 'down'
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_frame = 0
        self.roll_duration = 0
        self.roll_cooldown = 0
        self.pushback_cooldown = 0
        self.push_vx = 0
        self.push_vy = 0

    # Removed duplicate move method

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.is_moving:
            sprite = player_sprites[self.direction]['walk'][self.walk_frame]
        else:
            sprite = player_sprites[self.direction]['stand']

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, GREEN, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))
            text = self.font.render(self.direction, True, BLACK)
            screen.blit(text, (draw_x + 5, draw_y + 5))

    def move(self, keys):
        if self.roll_cooldown > 0:
            self.roll_cooldown -= 1
        if self.is_rolling:
            # Во время кувырка игнорируем новые нажатия клавиш, используем текущие dirx, diry, скорость 10
            self.x += int(self.dirx * 10)
            self.y += int(self.diry * 10)
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, self.x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, self.y))
            self.is_moving = True
            self.walk_timer += 1
            if self.walk_timer >= 10:
                self.walk_frame = (self.walk_frame + 1) % 4
                self.walk_timer = 0
            self.roll_timer += 1
            if self.roll_timer >= 10:
                self.roll_timer = 0
                self.roll_frame = (self.roll_frame + 1) % 4
            self.roll_duration += 1
        else:
            prev_x, prev_y = self.x, self.y
            self.diry = 0
            self.dirx = 0
            if keys[pygame.K_LEFT]:
                self.dirx = -1
                self.direction = 'left'
            if keys[pygame.K_RIGHT]:
                self.dirx = 1
                self.direction = 'right'
            if keys[pygame.K_UP]:
                self.diry = -1
                self.direction = 'up'
            if keys[pygame.K_DOWN]:
                self.diry = 1
                self.direction = 'down'
            length = (self.dirx ** 2 + self.diry ** 2) ** 0.5
            if length > 0:
                self.dirx /= length

                self.diry /= length
            self.x += int(self.dirx * self.speed)
            self.y += int(self.diry * self.speed)
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, self.x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, self.y))

            # Применение плавного отталкивания
            self.x = int(self.x + self.push_vx)
            self.y = int(self.y + self.push_vy)
            self.push_vx *= 0.85  # Затухание
            self.push_vy *= 0.85
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, self.x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, self.y))

            self.is_moving = (self.x != prev_x or self.y != prev_y)
            if self.is_moving:
                self.walk_timer += 1
                if self.walk_timer >= 10:
                    self.walk_frame = (self.walk_frame + 1) % 4
                    self.walk_timer = 0
            else:
                self.walk_frame = 0
            if keys[pygame.K_LSHIFT] and not self.is_rolling and self.roll_cooldown == 0:
                self.is_rolling = True
                self.roll_timer = 0
                self.roll_frame = 0

        if self.roll_duration >= 30:
            self.is_rolling = False
            self.roll_duration = 0
            self.roll_timer = 0
            self.roll_frame = 0
            self.roll_cooldown = 240

    def pushback(self, enemies, animals, bosses, pushback_waves, inventory, resources, day_night_cycle):
        if self.pushback_cooldown > 0:
            return
        self.pushback_cooldown = PUSHBACK_COOLDOWN
        player_center_x = self.x + PLAYER_SIZE // 2
        player_center_y = self.y + PLAYER_SIZE // 2

        # Создаём визуальный эффект
        pushback_waves.append(PushbackWave(player_center_x, player_center_y))

        # Воспроизводим звук удара при отталкивании
        sound_manager.play_random_punch()

        # Отталкиваем врагов (не боссов)
        for enemy in enemies[:]:
            enemy_center_x = enemy.x + PLAYER_SIZE // 2
            enemy_center_y = enemy.y + PLAYER_SIZE // 2
            dx = enemy_center_x - player_center_x
            dy = enemy_center_y - player_center_y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < PUSHBACK_RANGE and dist > 0:
                # Нормализуем направление и отталкиваем
                push_dx = (dx / dist) * PUSHBACK_FORCE * 5
                push_dy = (dy / dist) * PUSHBACK_FORCE * 5
                enemy.x = int(enemy.x + push_dx)
                enemy.y = int(enemy.y + push_dy)
                # Ограничиваем в пределах мира
                enemy.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, enemy.x))
                enemy.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, enemy.y))
                # Наносим урон
                enemy.hp -= PUSHBACK_DAMAGE
                if enemy.hp <= 0:
                    inventory['meat'] += 1
                    enemies.remove(enemy)
                    new_enemy = Enemy.spawn_enemy(resources + animals + enemies, day_night_cycle)
                    if new_enemy:
                        enemies.append(new_enemy)

        # Отталкиваем животных
        for animal in animals[:]:
            animal_center_x = animal.x + PLAYER_SIZE // 2
            animal_center_y = animal.y + PLAYER_SIZE // 2
            dx = animal_center_x - player_center_x
            dy = animal_center_y - player_center_y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < PUSHBACK_RANGE and dist > 0:
                # Нормализуем направление и отталкиваем
                push_dx = (dx / dist) * PUSHBACK_FORCE * 5
                push_dy = (dy / dist) * PUSHBACK_FORCE * 5
                animal.x = int(animal.x + push_dx)
                animal.y = int(animal.y + push_dy)
                # Ограничиваем в пределах мира
                animal.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, animal.x))
                animal.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, animal.y))
                # Наносим урон
                animal.hp -= PUSHBACK_DAMAGE
                if animal.hp <= 0:
                    inventory['food'] += 1
                    animals.remove(animal)
                    new_animal = Animal.spawn_animal(resources + animals, Animal.animal_types)
                    animals.append(new_animal)

        # Боссы НЕ отталкиваются, но получают урон если в радиусе
        for boss in bosses:
            boss_center_x = boss.x + boss.size // 2
            boss_center_y = boss.y + boss.size // 2
            dx = boss_center_x - player_center_x
            dy = boss_center_y - player_center_y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < PUSHBACK_RANGE:
                boss.hp -= PUSHBACK_DAMAGE

        print("Отталкивание активировано!")

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.is_rolling:
            sprite = player_sprites[self.direction]['roll'][self.roll_frame]
        elif self.is_moving:
            sprite = player_sprites[self.direction]['walk'][self.walk_frame]
        else:
            sprite = player_sprites[self.direction]['stand']

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, GREEN, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))