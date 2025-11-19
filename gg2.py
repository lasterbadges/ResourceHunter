import pygame
import sys
import random
import os
import json


# Инициализация Pygame
pygame.init()

# Constants
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

# Инициализация экрана и шрифта
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Survival Game")
font = pygame.font.SysFont(None, 24)
# Set up the screen
clock = pygame.time.Clock()

# Функции сохранения и загрузки
def save_game(player, inventory, tools, current_tool):
    data = {
        'player_x': player.x,
        'player_y': player.y,
        'player_hp': player.hp,
        'inventory': inventory,
        'tools': tools,
        'current_tool': current_tool
    }
    with open('save.json', 'w') as f:
        json.dump(data, f)

def load_game():
    try:
        with open('save.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None


# Загрузка изображений (теперь 5 фреймов: stand + 4 walk)
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


player_sprites = {}
directions = ['down', 'right', 'up', 'left']
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
cooldown_sprites = {'4': load_image('cooldown_4.png', size=(64, 32)), '3': load_image('cooldown_3.png', size=(64, 32)), '2': load_image('cooldown_2.png', size=(64, 32)), '1': load_image('cooldown_1.png', size=(64, 32)), 'ready': load_image('cooldown_ready.png', size=(64, 32))}

# Fallback для left: flip от right, если нет спрайтов
for key in ['stand', 'walk', 'roll']:
    if isinstance(player_sprites['right'][key], list):
        for i in range(len(player_sprites['right'][key])):
            if player_sprites['right'][key][i] is not None and not player_sprites['left'][key][i]:
                player_sprites['left'][key][i] = pygame.transform.flip(player_sprites['right'][key][i], True, False)
    else:
        if player_sprites['right'][key] is not None and not player_sprites['left'][key]:
            player_sprites['left'][key] = pygame.transform.flip(player_sprites['right'][key], True, False)



# Список типов животных (добавьте свои: ['cow', 'wolf', 'sheep'] и т.д.)
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
                animal_sprites[animal_type]['left'][key] = pygame.transform.flip(animal_sprites[animal_type]['right'][key], True, False)
            else:
                animal_sprites[animal_type]['left'][key] = None
        elif key == 'walk':
            animal_sprites[animal_type]['left'][key] = []
            for i in range(4):
                if animal_sprites[animal_type]['right'][key][i] is not None:
                    animal_sprites[animal_type]['left'][key].append(pygame.transform.flip(animal_sprites[animal_type]['right'][key][i], True, False))
                else:
                    animal_sprites[animal_type]['left'][key].append(None)

# Спрайты для врагов
enemy_sprites = {}
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
                enemy_sprites['left'][key].append(pygame.transform.flip(enemy_sprites['right'][key][i], True, False))
            else:
                enemy_sprites['left'][key].append(None)


tree_img = load_image("tree.png", (RESOURCE_SIZE, RESOURCE_SIZE))
rock_img = load_image("stone.png", (RESOURCE_SIZE, RESOURCE_SIZE))

# Загрузка текстур фона (3 ваших текстурки, assummed names: grass_tile1.png, grass_tile2.png, grass_tile3.png)
grass_tiles = [
    load_image("grass_tile1.png", (TILE_SIZE, TILE_SIZE)),
    load_image("grass_tile2.png", (TILE_SIZE, TILE_SIZE)),
    load_image("grass_tile3.png", (TILE_SIZE, TILE_SIZE))
]
# Удалить None если не загружено, или fallback
grass_tiles = [tile for tile in grass_tiles if tile]

# Загрузка изображений животных (расширяемо: список типов)
#animal_types = ['deer', 'wolf']  # Легко добавить новые, например 'bear'
#animal_images = {atype: load_image(f"{atype}.png", (PLAYER_SIZE, PLAYER_SIZE)) for atype in animal_types}

# Загрузка изображений врагов
enemy_img = load_image("enemy.png", (PLAYER_SIZE, PLAYER_SIZE))


# Класс Player с обновлённой анимацией
class Player:
    def __init__(self):
        self.font = font
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        self.speed = 5
        self.dirx = 0
        self.diry = 0
        self.hp = 100
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
            text = self.font.render(self.direction, True, BLACK)
            screen.blit(text, (draw_x + 5, draw_y + 5))

# Resource class (без изменений)
class Resource:
    def __init__(self, x, y, type_):
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
            img = tree_img if self.type == 'tree' else rock_img
            if img:
                screen.blit(img, (draw_x, draw_y))
            else:
                color = BROWN if self.type == 'tree' else GRAY
                pygame.draw.rect(screen, color, (draw_x, draw_y, RESOURCE_SIZE, RESOURCE_SIZE))



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
            color = (0, 255, 0) if self.type == 'cow' else (128, 128, 128)  # Разные цвета для типов
            pygame.draw.rect(screen, color, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))

        # Полоска здоровья
        bar_width = PLAYER_SIZE
        bar_height = 5
        bar_x = draw_x
        bar_y = draw_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.hp / 10) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))

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
            return False
        if (abs(new_x - player.x) < PLAYER_SIZE and
                abs(new_y - player.y) < PLAYER_SIZE):
            return False
        for enemy in enemies:
            if enemy != self:
                if (abs(new_x - enemy.x) < PLAYER_SIZE-15 and
                        abs(new_y - enemy.y) < PLAYER_SIZE-15):
                    return False
        return True

    def move_towards_player(self, player_x, player_y, resources, enemies, player):
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

    def attack_player(self, player, dt):
        if not self.agro:
            return  # Не атакуем, если нет АГРО
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        if distance <= ATTACK_RANGE and self.attack_timer <= 0:
            player.hp -= self.damage  # Предполагаем player.hp; замените на player.health если нужно
            self.attack_timer = 120
        elif self.attack_timer > 0:
            self.attack_timer -= 1

    def draw(self, screen, camera_x, camera_y):
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




button_width = 376
button_height = 103
button_x = screen_width // 2 - button_width // 2
start_button = pygame.Rect(button_x, screen_height // 2 - 100, button_width, button_height)
settings_button = pygame.Rect(button_x, screen_height // 2, button_width, button_height)
quit_button = pygame.Rect(button_x, screen_height // 2 + 100, button_width, button_height)


def draw_menu(player, resources, animals, enemies, camera_x, camera_y):
    # Отрисовываем геймплей в качестве фона меню
    screen.fill(GRASS_GREEN)

    # Отрисовка фона (травы) - аналогично основной игре
    start_x = camera_x // TILE_SIZE
    start_y = camera_y // TILE_SIZE
    end_x = (camera_x + screen_width) // TILE_SIZE + 1
    end_y = (camera_y + screen_height) // TILE_SIZE + 1

    for tile_x in range(start_x, end_x):
        for tile_y in range(start_y, end_y):
            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                draw_x = world_x - camera_x
                draw_y = world_y - camera_y

                random.seed(tile_x * 12345 + tile_y * 67890)
                if grass_tiles:
                    variant = random.choice(grass_tiles)
                    if variant:
                        screen.blit(variant, (draw_x, draw_y))
                    else:
                        pygame.draw.rect(screen, GRASS_GREEN, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, GRASS_GREEN, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))

    # Отрисовываем игровые объекты
    for res in resources:
        res.draw(screen, camera_x, camera_y)
    for animal in animals:
        animal.draw(screen, camera_x, camera_y)
    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y)

    # Добавляем полупрозрачный оверлей для лучшей читаемости меню
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Полупрозрачный черный
    screen.blit(overlay, (0, 0))

    # Заголовок игры
    title_text = font.render("Resource hunter", True, WHITE)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 200))

    # Кнопки меню
    def ButtonMenuDrawer(name: str, Num: int = 0):
        start_button = pygame.Rect(button_x, screen_height // 3 + 105 * Num, button_width, button_height)
        start_button_image = pygame.image.load(name).convert_alpha()
        screen.blit(start_button_image, start_button)

    # Start Game button
    ButtonMenuDrawer("Play.png")

    # Settings button
    ButtonMenuDrawer("Settings.png", 1)

    # Quit button
    ButtonMenuDrawer("Exit.png", 2)




def handle_menu_events(events):
    global game_state, previous_state
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            mouse_pos = pygame.mouse.get_pos()

            # Проверка коллизий и изменение состояния
            if start_button.collidepoint(mouse_pos):
                game_state = 'game'

            elif settings_button.collidepoint(mouse_pos):
                previous_state = 'menu'
                game_state = 'settings'

            elif quit_button.collidepoint(mouse_pos):

                pygame.quit()
                sys.exit()

def draw_settings():
    # Полупрозрачный фон
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill(SEMI_BLACK)
    screen.blit(overlay, (0, 0))
    # Заголовок
    title = font.render("Settings", True, WHITE)
    screen.blit(title, (screen_width//2 - 50, screen_height//2 - 150))
    # Кнопки разрешений
    res1_button = pygame.Rect(screen_width//2 - 100, screen_height//2 - 100, 200, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, res1_button)
    res1_text = font.render("800x800", True, BLACK)
    screen.blit(res1_text, (res1_button.x + 50, res1_button.y + 15))

    res2_button = pygame.Rect(screen_width//2 - 100, screen_height//2 - 30, 200, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, res2_button)
    res2_text = font.render("1024x768", True, BLACK)
    screen.blit(res2_text, (res2_button.x + 40, res2_button.y + 15))

    res3_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 40, 200, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, res3_button)
    res3_text = font.render("1280x720", True, BLACK)
    screen.blit(res3_text, (res3_button.x + 40, res3_button.y + 15))

    back_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 110, 200, 50)
    pygame.draw.rect(screen, RED, back_button)
    back_text = font.render("Back", True, BLACK)
    screen.blit(back_text, (back_button.x + 70, back_button.y + 15))

def handle_settings_events(events):
    global game_state, previous_state, screen_width, screen_height, screen
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            res1_button = pygame.Rect(screen_width//2 - 100, screen_height//2 - 100, 200, 50)
            res2_button = pygame.Rect(screen_width//2 - 100, screen_height//2 - 30, 200, 50)
            res3_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 40, 200, 50)
            back_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 110, 200, 50)
            if res1_button.collidepoint(mouse_pos):
                screen_width, screen_height = 800, 800
                screen = pygame.display.set_mode((screen_width, screen_height))
                print(f"Resolution changed to {screen_width}x{screen_height}")
            elif res2_button.collidepoint(mouse_pos):
                screen_width, screen_height = 1024, 768
                screen = pygame.display.set_mode((screen_width, screen_height))
                print(f"Resolution changed to {screen_width}x{screen_height}")
            elif res3_button.collidepoint(mouse_pos):
                screen_width, screen_height = 1280, 720
                screen = pygame.display.set_mode((screen_width, screen_height))
                print(f"Resolution changed to {screen_width}x{screen_height}")
            elif back_button.collidepoint(mouse_pos):
                game_state = previous_state
                print(f"Returning to {previous_state} from settings")





def draw_pause():
    # Полупрозрачный фон для паузы
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill(SEMI_BLACK)
    screen.blit(overlay, (0, 0))

    # Заголовок паузы
    pause_text = font.render("Paused", True, WHITE)
    screen.blit(pause_text, (screen_width // 2 - pause_text.get_width() // 2, screen_height // 2 - 150))

    # Кнопки паузы
    button_width = 200
    button_height = 50
    button_x = screen_width // 2 - button_width // 2

    # Resume button
    resume_button = pygame.Rect(button_x, screen_height // 2 - 50, button_width, button_height)
    pygame.draw.rect(screen, GREEN, resume_button)
    resume_text = font.render("Resume", True, BLACK)
    screen.blit(resume_text, (resume_button.x + (button_width - resume_text.get_width()) // 2, resume_button.y + (button_height - resume_text.get_height()) // 2))

    # Settings button
    settings_button = pygame.Rect(button_x, screen_height // 2 + 20, button_width, button_height)
    pygame.draw.rect(screen, LIGHT_GRAY, settings_button)
    settings_text = font.render("Settings", True, BLACK)
    screen.blit(settings_text, (settings_button.x + (button_width - settings_text.get_width()) // 2, settings_button.y + (button_height - settings_text.get_height()) // 2))

    # Quit to Menu button
    quit_menu_button = pygame.Rect(button_x, screen_height // 2 + 90, button_width, button_height)
    pygame.draw.rect(screen, RED, quit_menu_button)
    quit_menu_text = font.render("Quit to Menu", True, BLACK)
    screen.blit(quit_menu_text, (quit_menu_button.x + (button_width - quit_menu_text.get_width()) // 2, quit_menu_button.y + (button_height - quit_menu_text.get_height()) // 2))

def handle_pause_events(events):
    global game_state, previous_state, inventory, tools, current_tool, player
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            mouse_pos = pygame.mouse.get_pos()
            # Определение прямоугольников кнопок (должны совпадать с draw_pause)
            button_width = 200
            button_height = 50
            button_x = screen_width // 2 - button_width // 2
            resume_button = pygame.Rect(button_x, screen_height // 2 - 50, button_width, button_height)
            settings_button = pygame.Rect(button_x, screen_height // 2 + 20, button_width, button_height)
            quit_menu_button = pygame.Rect(button_x, screen_height // 2 + 90, button_width, button_height)

            # Проверка коллизий и изменение состояния
            if resume_button.collidepoint(mouse_pos):
                game_state = 'game'
                print("Возобновление игры.")
            elif settings_button.collidepoint(mouse_pos):
                previous_state = 'pause'
                game_state = 'settings'
                print("Переход в настройки из паузы.")
            elif quit_menu_button.collidepoint(mouse_pos):
                save_game(player, inventory, tools, current_tool)  # Сохранение при выходе в меню
                game_state = 'menu'
                print("Возврат в меню.")

def draw_game_over():
    # Полупрозрачный фон
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill(SEMI_BLACK)
    screen.blit(overlay, (0, 0))

    # Заголовок
    title = font.render("Game Over", True, RED)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, screen_height // 2 - 150))

    # Кнопки
    button_width = 200
    button_height = 50
    button_x = screen_width // 2 - button_width // 2

    respawn_button = pygame.Rect(button_x, screen_height // 2 - 50, button_width, button_height)
    pygame.draw.rect(screen, GREEN, respawn_button)
    respawn_text = font.render("Respawn", True, BLACK)
    screen.blit(respawn_text, (respawn_button.x + (button_width - respawn_text.get_width()) // 2, respawn_button.y + (button_height - respawn_text.get_height()) // 2))

    quit_button = pygame.Rect(button_x, screen_height // 2 + 20, button_width, button_height)
    pygame.draw.rect(screen, RED, quit_button)
    quit_text = font.render("Quit to Menu", True, BLACK)
    screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2, quit_button.y + (button_height - quit_text.get_height()) // 2))

def handle_game_over_events(events):
    global game_state, player, inventory, tools, current_tool
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            button_width = 200
            button_height = 50
            button_x = screen_width // 2 - button_width // 2
            respawn_button = pygame.Rect(button_x, screen_height // 2 - 50, button_width, button_height)
            quit_button = pygame.Rect(button_x, screen_height // 2 + 20, button_width, button_height)

            if respawn_button.collidepoint(mouse_pos):
                # Respawn: сброс hp, позиция, инвентарь, инструменты
                player.hp = 100
                player.hunger_timer = 0
                player.x = WORLD_WIDTH // 2
                player.y = WORLD_HEIGHT // 2
                inventory = {'wood': 0, 'stone': 0, 'food': 0, 'meat': 0}
                tools = {'hand': True, 'axe': False, 'pickaxe': False, 'sword': False}
                current_tool = 'hand'
                game_state = 'game'
                print("Respawned.")
            elif quit_button.collidepoint(mouse_pos):
                save_game(player, inventory, tools, current_tool)  # Сохранение
                game_state = 'menu'
                print("Quit to menu.")

# Spawn resource with distance check
def spawn_resource(existing_resources):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - RESOURCE_SIZE)
        y = random.randint(0, WORLD_HEIGHT - RESOURCE_SIZE)
        type_ = random.choice(['tree', 'rock'])
        candidate = Resource(x, y, type_)
        # Проверяем расстояние до существующих ресурсов
        too_close = False
        for res in existing_resources:
            dx = candidate.x - res.x
            dy = candidate.y - res.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < MIN_DISTANCE:
                too_close = True
                break
        if not too_close:
            return candidate
    # Если не удалось, спавним в любом случае
    x = random.randint(0, WORLD_WIDTH - RESOURCE_SIZE)
    y = random.randint(0, WORLD_HEIGHT - RESOURCE_SIZE)
    type_ = random.choice(['tree', 'rock'])
    return Resource(x, y, type_)


# Spawn animal with distance check (обновлено для type)
def spawn_animal(existing_objects, animal_types):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
        y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
        animal_type = random.choice(animal_types)
        candidate = Animal(x, y, animal_type)
        # Проверяем расстояние до ресурсов и других животных
        too_close = False
        for obj in existing_objects:
            dx = candidate.x - obj.x
            dy = candidate.y - obj.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < MIN_DISTANCE:
                too_close = True
                break
        if not too_close:
            return candidate
    # Если не удалось, спавним в любом случае
    x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
    y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
    animal_type = random.choice(animal_types)
    return Animal(x, y, animal_type)


# Spawn enemy (аналогично)
def spawn_enemy(existing_objects):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
        y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
        candidate = Enemy(x, y)
        too_close = False
        for obj in existing_objects:
            dx = candidate.x - obj.x
            dy = candidate.y - obj.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < MIN_DISTANCE:
                too_close = True
                break
        if not too_close:
            return candidate
    x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
    y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
    return Enemy(x, y)


def update_camera(player, camera_x, camera_y):
    camera_x = max(0, min(WORLD_WIDTH - screen_width, player.x - screen_width // 2))
    camera_y = max(0, min(WORLD_HEIGHT - screen_height, player.y - screen_height // 2))
    return camera_x, camera_y


# Функция для рисования меню инвентаря (обновлено: добавлен Meat)
def draw_inventory_menu(screen, inventory, menu_pos):
    # Полупрозрачный фон
    menu_surf = pygame.Surface((MENU_WIDTH, MENU_HEIGHT), pygame.SRCALPHA)
    menu_surf.fill(SEMI_BLACK)
    screen.blit(menu_surf, menu_pos)

    # Заголовок
    title = font.render("Инвентарь", True, WHITE)
    screen.blit(title, (menu_pos[0] + 10, menu_pos[1] + 10))

    # Ресурсы
    inv_y = menu_pos[1] + 50
    screen.blit(font.render(f"Дерево: {inventory['wood']}", True, WHITE), (menu_pos[0] + 10, inv_y))
    screen.blit(font.render(f"Камень: {inventory['stone']}", True, WHITE), (menu_pos[0] + 10, inv_y + 30))
    screen.blit(font.render(f"Еда: {inventory['food']}", True, WHITE), (menu_pos[0] + 10, inv_y + 60))
    screen.blit(font.render(f"Мясо: {inventory['meat']}", True, WHITE), (menu_pos[0] + 10, inv_y + 90))  # Новое: Мясо


# Функция для рисования меню крафта (обновлено для меча)
def draw_craft_menu(screen, inventory, tools, menu_pos):
    # Полупрозрачный фон
    menu_surf = pygame.Surface((MENU_WIDTH, MENU_HEIGHT), pygame.SRCALPHA)
    menu_surf.fill(SEMI_BLACK)
    screen.blit(menu_surf, menu_pos)

    # Заголовок
    title = font.render("Крафт", True, WHITE)
    screen.blit(title, (menu_pos[0] + 10, menu_pos[1] + 10))

    # Кнопки крафтов
    button_y = menu_pos[1] + 50
    buttons = []

    # Топор
    if not tools['axe']:
        axe_req = "3 дерева, 2 камня"
        can_craft_axe = inventory['wood'] >= 3 and inventory['stone'] >= 2
        button_color = GREEN if can_craft_axe else GRAY
        axe_text = font.render("Скрафтить", True, WHITE)
        axe_button = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, button_color, axe_button)
        screen.blit(font.render("Топор:", True, WHITE), (menu_pos[0] + 10, button_y - 20))
        screen.blit(font.render(axe_req, True, WHITE), (menu_pos[0] + 80, button_y - 20))
        screen.blit(axe_text, (axe_button.x + 10, axe_button.y + 10))
        buttons.append(('axe', axe_button, can_craft_axe))
        button_y += BUTTON_HEIGHT + 10
    else:
        screen.blit(font.render("Топор: ✓", True, GREEN), (menu_pos[0] + 10, button_y))
        button_y += 30

    # Кирка
    if not tools['pickaxe']:
        pick_req = "3 камня, 2 дерева"
        can_craft_pick = inventory['stone'] >= 3 and inventory['wood'] >= 2
        button_color = GREEN if can_craft_pick else GRAY
        pick_text = font.render("Скрафтить", True, WHITE)
        pick_button = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, button_color, pick_button)
        screen.blit(font.render("Кирка:", True, WHITE), (menu_pos[0] + 10, button_y - 20))
        screen.blit(font.render(pick_req, True, WHITE), (menu_pos[0] + 80, button_y - 20))
        screen.blit(pick_text, (pick_button.x + 10, pick_button.y + 10))
        buttons.append(('pickaxe', pick_button, can_craft_pick))
        button_y += BUTTON_HEIGHT + 10
    else:
        screen.blit(font.render("Кирка: ✓", True, GREEN), (menu_pos[0] + 10, button_y))
        button_y += 30

    # Меч (новое)
    if not tools['sword']:
        sword_req = "4 дерева, 5 камней"
        can_craft_sword = inventory['wood'] >= 4 and inventory['stone'] >= 5
        button_color = GREEN if can_craft_sword else GRAY
        sword_text = font.render("Скрафтить", True, WHITE)
        sword_button = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, button_color, sword_button)
        screen.blit(font.render("Меч:", True, WHITE), (menu_pos[0] + 10, button_y - 20))
        screen.blit(font.render(sword_req, True, WHITE), (menu_pos[0] + 80, button_y - 20))
        screen.blit(sword_text, (sword_button.x + 10, sword_button.y + 10))
        buttons.append(('sword', sword_button, can_craft_sword))
    else:
        screen.blit(font.render("Меч: ✓", True, GREEN), (menu_pos[0] + 10, button_y))
        button_y += 30

    return buttons  # Возвращаем кнопки для обработки кликов


# Функция для обработки крафта (обновлено для меча)
def handle_craft(tool_name, inventory, tools):
    if tool_name == 'axe' and inventory['wood'] >= 3 and inventory['stone'] >= 2 and not tools['axe']:
        inventory['wood'] -= 3
        inventory['stone'] -= 2
        tools['axe'] = True
        print("Топор скрафчен! 🎉")
        return True
    elif tool_name == 'pickaxe' and inventory['stone'] >= 3 and inventory['wood'] >= 2 and not tools['pickaxe']:
        inventory['stone'] -= 3
        inventory['wood'] -= 2
        tools['pickaxe'] = True
        print("Кирка скрафчена! 🛠️")
        return True
    elif tool_name == 'sword' and inventory['wood'] >= 4 and inventory['stone'] >= 5 and not tools['sword']:
        inventory['wood'] -= 4
        inventory['stone'] -= 5
        tools['sword'] = True
        print("Меч скрафчен! ⚔️")
        return True
    else:
        print("Недостаточно ресурсов или инструмент уже скрафчен!")
        return False


def main():
    global game_state
    global screen_width, screen_height, screen, menu_bg, game_state
    global player
    global inventory
    global tools
    global current_tool

    player = Player()
    game_state = 'menu'
    previous_state = None
    inventory = {'wood': 0, 'stone': 0, 'food': 0, 'meat': 0}  # Новое: добавлено 'meat' для убоины врагов
    tools = {'hand': True, 'axe': False, 'pickaxe': False, 'sword': False}
    current_tool = 'hand'
    space_cooldown = 0  # **Новое: cooldown для SPACE в мс**

    menu_camera_x = 0
    menu_camera_y = 0
    menu_player = Player()  # Специальный игрок для меню
    menu_player.x = WORLD_WIDTH // 2
    menu_player.y = WORLD_HEIGHT // 2

    # Создаем отдельные наборы объектов для меню
    menu_resources = []
    for _ in range(20):
        new_res = spawn_resource(menu_resources)
        menu_resources.append(new_res)

    menu_animals = []
    for _ in range(10):
        new_animal = spawn_animal(menu_resources + menu_animals, animal_types)
        menu_animals.append(new_animal)

    menu_enemies = []
    for _ in range(5):
        new_enemy = spawn_enemy(menu_resources + menu_animals + menu_enemies)
        menu_enemies.append(new_enemy)

    # Инициализируем камеру меню
    menu_camera_x, menu_camera_y = update_camera(menu_player, menu_camera_x, menu_camera_y)

    # pygame.mixer.music.load("background_music.mp3")
    # pygame.mixer.music.play(0)

    # Загрузка сохранения
    save_data = load_game()
    if save_data:
        player.x = save_data.get('player_x', player.x)
        player.y = save_data.get('player_y', player.y)
        player.hp = save_data.get('player_hp', player.hp)
        inventory.update(save_data.get('inventory', {}))
        tools.update(save_data.get('tools', {}))
        current_tool = save_data.get('current_tool', current_tool)

    # Спавн ресурсов с проверкой расстояния
    resources = []
    for _ in range(20):
        new_res = spawn_resource(resources)
        resources.append(new_res)

    # Спавн животных с проверкой расстояния (новые виды)
    animals = []
    for _ in range(10):  # 10 животных
        new_animal = spawn_animal(resources + animals, animal_types)
        animals.append(new_animal)

    # Спавн врагов
    enemies = []
    for _ in range(5):
        new_enemy = spawn_enemy(resources + animals + enemies)
        enemies.append(new_enemy)

    camera_x = 0
    camera_y = 0
    inventory_open = False  # Флаг меню инвентаря
    craft_open = False  # Флаг меню крафта

    menu_pos = ((screen_width - MENU_WIDTH) // 2, (screen_height - MENU_HEIGHT) // 2)  # Центр экрана

    last_time = pygame.time.get_ticks()



    f = 1  # Управляющий фактор направления для фона меню (1: вправо, -1: влево)
    running = True
    while running:
        # Музыка
        # if game_state in ['menu', 'pause']:
        # if not pygame.mixer.music.get_busy():
        # pygame.mixer.music.play(-1)
        # else:
        # pygame.mixer.music.stop()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Обработка событий в зависимости от состояния
        if game_state == 'menu':
            handle_menu_events(events)

            # 1. Движение игрока в меню (ИСПРАВЛЕНО ДЛЯ РЕВЕРСА и АНИМАЦИИ)
            move_speed = 3  # Увеличим скорость для более очевидного движения
            menu_player.x += move_speed * f

            # Обновление состояния анимации (чтобы игрок не выглядел стоящим)
            menu_player.is_moving = True
            menu_player.direction = 'right' if f > 0 else 'left'
            menu_player.walk_timer += 1
            if menu_player.walk_timer >= 10:
                menu_player.walk_frame = (menu_player.walk_frame + 1) % 4
                menu_player.walk_timer = 0

            # Проверка границ и реверс направления
            if f > 0 and menu_player.x >= WORLD_WIDTH - PLAYER_SIZE:
                f = -1  # Движение влево
                menu_player.x = WORLD_WIDTH - PLAYER_SIZE  # Коррекция, чтобы избежать выхода за границу
            elif f < 0 and menu_player.x <= 0:
                f = 1  # Движение вправо
                menu_player.x = 0  # Коррекция

            # 2. Обновляем движение животных
            for animal in menu_animals:
                animal.move(menu_resources)

            # 3. Обновляем движение врагов
            for enemy in menu_enemies:
                # В меню они просто бродят
                enemy.move_randomly(menu_resources, menu_enemies, menu_player)

            # 4. Обновляем камеру меню, чтобы она следовала за игроком
            menu_camera_x, menu_camera_y = update_camera(menu_player, menu_camera_x, menu_camera_y)

            # 5. Отрисовка фона меню
            draw_menu(menu_player, menu_resources, menu_animals, menu_enemies, menu_camera_x, menu_camera_y)
        elif game_state == 'settings':
            handle_settings_events(events)
        elif game_state == 'pause':
            handle_pause_events(events)
        elif game_state == 'game_over':
            handle_game_over_events(events)

        # Рисование в зависимости от состояния
        if game_state == "main":
            draw_menu(menu_player, menu_resources, menu_animals, menu_enemies, menu_camera_x, menu_camera_y)
        elif game_state == 'game':
            try:
                current_time = pygame.time.get_ticks()
                dt = current_time - last_time
                last_time = current_time

                # Обновление cooldown для SPACE
                space_cooldown = max(0, space_cooldown - dt)

                # Система голода
                player.hunger_timer += dt
                if player.hunger_timer > 60000:  # Каждые 5 секунд
                    player.hp -= 1
                    player.hunger_timer = 0
                    if player.hp <= 0:
                        game_state = 'game_over'

                # ИСПРАВЛЕННАЯ ОТРИСОВКА ФОНА
                # Очистка экрана
                screen.fill(GRASS_GREEN)

                # Расчет правильных границ для отрисовки тайлов
                start_x = camera_x // TILE_SIZE
                start_y = camera_y // TILE_SIZE
                end_x = (camera_x + screen_width) // TILE_SIZE + 1
                end_y = (camera_y + screen_height) // TILE_SIZE + 1

                # Отрисовка только видимых тайлов
                for tile_x in range(start_x, end_x):
                    for tile_y in range(start_y, end_y):
                        world_x = tile_x * TILE_SIZE
                        world_y = tile_y * TILE_SIZE

                        # Проверка, что тайл в пределах мира
                        if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                            # Вычисляем позицию для отрисовки на экране
                            draw_x = world_x - camera_x
                            draw_y = world_y - camera_y

                            # Выбираем случайный тайл (детерминировано)
                            random.seed(tile_x * 12345 + tile_y * 67890)
                            if grass_tiles:
                                variant = random.choice(grass_tiles)
                                if variant:
                                    screen.blit(variant, (draw_x, draw_y))
                                else:
                                    pygame.draw.rect(screen, GRASS_GREEN, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                            else:
                                pygame.draw.rect(screen, GRASS_GREEN, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))

                keys = pygame.key.get_pressed()

                # ESC для паузы
                if keys[pygame.K_ESCAPE]:
                    game_state = 'pause'
                    print("Transitioning to pause state")
                    pygame.time.wait(200)

                # Управление меню (без изменений)
                if keys[pygame.K_i]:
                    inventory_open = not inventory_open
                    print("Меню инвентаря:", "открыто" if inventory_open else "закрыто")
                    pygame.time.wait(200)  # Задержка
                if keys[pygame.K_c]:
                    craft_open = not craft_open
                    print("Меню крафта:", "открыто" if craft_open else "закрыто")
                    pygame.time.wait(200)  # Задержка

                # Смена инструментов (только если меню закрыты)
                elif keys[pygame.K_t] and not inventory_open and not craft_open:
                    tool_list = [k for k, v in tools.items() if v]
                    if tool_list:
                        current_index = tool_list.index(current_tool)
                        current_tool = tool_list[(current_index + 1) % len(tool_list)]

                if keys[pygame.K_f] and inventory['food'] > 0:
                    player.hp = min(100, player.hp + 20)
                    inventory['food'] -= 1

                if keys[pygame.K_m] and inventory['meat'] > 0:
                    player.hp = min(100, player.hp + 30)
                    inventory['meat'] -= 1

                # Обновление движения животных перед player.move
                for animal in animals:
                    animal.move(resources)

                # Обновление движения и атаки врагов
                for enemy in enemies:
                    enemy.move_towards_player(player.x, player.y, resources, enemies, player)
                    enemy.attack_player(player, dt)

                if player.hp <= 0:
                    game_state = 'game_over'

                player.move(keys)

                camera_x, camera_y = update_camera(player, camera_x, camera_y)

                # Gathering logic для ресурсов (обновлено: проверка cooldown и устранение wait)
                for res in resources[:]:
                    player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
                    res_rect = pygame.Rect(res.x, res.y, RESOURCE_SIZE, RESOURCE_SIZE)
                    if player_rect.colliderect(res_rect) and keys[pygame.K_SPACE] and space_cooldown <= 0:
                        print(f"DEBUG: Colliding with resource at ({res.x}, {res.y}), type: {res.type}")
                        if res.take_damage(current_tool):
                            if res.type == 'tree':
                                inventory['wood'] += 1
                            elif res.type == 'rock':
                                inventory['stone'] += 1
                            resources.remove(res)
                            new_res = spawn_resource(resources)
                            resources.append(new_res)
                            print(f"DEBUG: Собрано {res.type}! Новый ресурс заспавнен с проверкой расстояния!")
                        # **Удалено: pygame.time.wait(200)**
                        space_cooldown = 200  # **Новое: устанавливаем 1-секундный cooldown**

                # Gathering logic для животных (обновлено аналогично)
                for animal in animals[:]:
                    player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
                    animal_rect = pygame.Rect(animal.x, animal.y, PLAYER_SIZE, PLAYER_SIZE)
                    if player_rect.colliderect(animal_rect) and keys[pygame.K_SPACE] and space_cooldown <= 0:
                        print(f"DEBUG: Colliding with animal at ({animal.x}, {animal.y}), type: {animal.type}")
                        damage = 5 if current_tool == 'sword' else 1
                        animal.hp -= damage
                        if animal.hp <= 0:
                            inventory['food'] += 1
                            animals.remove(animal)
                            new_animal = spawn_animal(resources + animals, animal_types)
                            animals.append(new_animal)
                            print(f"DEBUG: {animal.type} убито! Food +1")
                            # **Удалено: pygame.time.wait(200)**
                        space_cooldown = 200  # **Новое: 1-секундный cooldown**

                # Gathering logic для врагов (обновлено аналогично)
                for enemy in enemies[:]:
                    distance = ((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2) ** 0.5
                    if distance <= ATTACK_RANGE and keys[pygame.K_SPACE] and space_cooldown <= 0:
                        print(f"DEBUG: Attacking enemy at ({enemy.x}, {enemy.y}), distance: {distance}")
                        damage = 5 if current_tool == 'sword' else 2
                        enemy.hp -= damage
                        if enemy.hp <= 0:
                            inventory['meat'] += 1
                            enemies.remove(enemy)
                            new_enemy = spawn_enemy(resources + animals + enemies)
                            enemies.append(new_enemy)
                            print("DEBUG: Враг убит! Meat +1")
                            # **Удалено: pygame.time.wait(200)**
                        space_cooldown = 200  # **Новое: 1-секундный cooldown**

                # Рисуем мир
                for res in resources:
                    res.draw(screen, camera_x, camera_y)
                for animal in animals:
                    animal.draw(screen, camera_x, camera_y)  # Добавлено рисование животных
                for enemy in enemies:
                    enemy.draw(screen, camera_x, camera_y)  # Рисуем врагов
                player.draw(screen, camera_x, camera_y)

                # Визуальный таймер cooldown кувырка
                key = str((player.roll_cooldown + 59) // 60) if player.roll_cooldown > 0 else 'ready'
                screen.blit(cooldown_sprites[key], (screen_width - 100, 50))

                # UI (только если меню закрыты)
                if not inventory_open and not craft_open:
                    tool_text = f"Инструмент: {current_tool}"
                    screen.blit(font.render(tool_text, True, BLACK), (10, 10))
                    health_text = f"Здоровье: {player.hp}"
                    screen.blit(font.render(health_text, True, BLACK), (10, 40))
                    pos_text = f"Позиция: ({player.x}, {player.y})"
                    screen.blit(font.render(pos_text, True, BLACK), (10, 70))
                    hint_text = font.render("Нажми I для инвентаря\nНажми C для крафта", True, BLACK)
                    screen.blit(hint_text, (10, 100))

                # Рисуем меню инвентаря (если открыто)
                if inventory_open:
                    draw_inventory_menu(screen, inventory, menu_pos)
                    close_text = font.render("Нажми I для закрытия", True, WHITE)
                    screen.blit(close_text, (menu_pos[0] + 10, menu_pos[1] + MENU_HEIGHT - 30))

                # Рисуем меню крафта (если открыто)
                if craft_open:
                    buttons = draw_craft_menu(screen, inventory, tools, menu_pos)

                    # Обработка кликов (если ЛКМ зажата и кнопка активна)
                    if pygame.mouse.get_pressed()[0]:
                        mouse_pos = pygame.mouse.get_pos()
                        for tool_name, button_rect, can_craft in buttons:
                            if button_rect.collidepoint(mouse_pos) and can_craft:
                                handle_craft(tool_name, inventory, tools)
                                pygame.time.wait(200)  # Задержка для фидбека
                                break  # Только один крафт за клик
                    close_text = font.render("Нажми C для закрытия", True, WHITE)
                    screen.blit(close_text, (menu_pos[0] + 10, menu_pos[1] + MENU_HEIGHT - 30))
            except Exception as e:
                print(f"Error in game: {e}")
        elif game_state == 'settings':
            draw_settings()
        elif game_state == 'pause':
            draw_pause()
        elif game_state == 'game_over':
            draw_game_over()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()