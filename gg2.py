import pygame
import sys
import random
import os


# Инициализация Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
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
ATTACK_RANGE = 100  # Радиус атаки для врагов

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Survival Game")
font = pygame.font.SysFont(None, 24)
# Set up the screen
clock = pygame.time.Clock()


# Загрузка изображений (теперь 5 фреймов: stand + 4 walk)
def load_image(filename, size):
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        try:
            img = pygame.image.load(filepath).convert_alpha()
            return pygame.transform.scale(img, size)
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
        ]
    }

# Fallback для left: flip от right, если нет спрайтов
for key in player_sprites['right']:
    if isinstance(player_sprites['right'][key], list):
        for i in range(len(player_sprites['right'][key])):
            if not player_sprites['left'][key][i]:
                player_sprites['left'][key][i] = pygame.transform.flip(player_sprites['right'][key][i], True, False)
    else:
        if not player_sprites['left'][key]:
            player_sprites['left'][key] = pygame.transform.flip(player_sprites['right'][key], True, False)

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
animal_types = ['deer', 'wolf']  # Легко добавить новые, например 'bear'
animal_images = {atype: load_image(f"{atype}.png", (PLAYER_SIZE, PLAYER_SIZE)) for atype in animal_types}

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
        self.health = 100
        self.direction = 'down'
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0

    def move(self, keys):
        self.diry = 0
        self.dirx = 0
        prev_x, prev_y = self.x, self.y
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
        prev_x, prev_y = self.x, self.y
        self.diry = 0
        self.dirx = 0
        prev_x, prev_y = self.x, self.y
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
        if 0 <= draw_x <= SCREEN_WIDTH and 0 <= draw_y <= SCREEN_HEIGHT:
            img = tree_img if self.type == 'tree' else rock_img
            if img:
                screen.blit(img, (draw_x, draw_y))
            else:
                color = BROWN if self.type == 'tree' else GRAY
                pygame.draw.rect(screen, color, (draw_x, draw_y, RESOURCE_SIZE, RESOURCE_SIZE))


# Новый класс Animal с HP, types
class Animal:
    def __init__(self, x, y, animal_type):
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = random.choice(['down', 'right', 'up', 'left'])
        self.move_timer = 0
        self.hp = 10  # Добавлено HP
        self.type = animal_type  # Тип животного

    def move(self, resources):  # Избегать ресурсов для простоты
        self.move_timer += 1
        if self.move_timer >= 60:  # Сменить направление каждые ~1 сек (60 кадров)
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

        # Простая проверка столкновений (не заходить в ресурсы)
        can_move = True
        for res in resources:
            if abs(new_x - res.x) < RESOURCE_SIZE and abs(new_y - res.y) < RESOURCE_SIZE:
                can_move = False
                break

        if can_move:
            self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, new_x))
            self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, new_y))

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        img = animal_images.get(self.type)
        if img:
            screen.blit(img, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, GREEN, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))  # Green fallback


# Класс Enemy (враг, атакующий игрока в радиусе)
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3  # Немного быстрее
        self.hp = 30  # Пример HP для врага
        self.damage = 6
        self.attack_timer = 0  # Для атаки каждые 2 сек
        self.direction = random.choice(['down', 'right', 'up', 'left'])
        self.move_timer = 0

    def can_move_to_position(self, new_x, new_y, resources, enemies, player):
        """Проверяет, может ли враг переместиться в новую позицию"""

        # 1. Проверка границ мира
        if (new_x < 0 or new_x > WORLD_WIDTH - PLAYER_SIZE or
                new_y < 0 or new_y > WORLD_HEIGHT - PLAYER_SIZE):
            return False
        if (abs(new_x - player.x) < PLAYER_SIZE and
                abs(new_y - player.y) < PLAYER_SIZE):
            return False

        # 4. Проверка столкновения с другими врагами
        for enemy in enemies:
            if enemy != self:  # Не проверяем столкновение с самим собой
                if (abs(new_x - enemy.x) < PLAYER_SIZE-5 and
                        abs(new_y - enemy.y) < PLAYER_SIZE):
                    return False

        return True

    def move_towards_player(self, player_x, player_y, resources, enemies, player):
        dx = max(-self.speed, min(self.speed, player_x- self.x))
        dy = max(-self.speed, min(self.speed, player_y - self.y))
        new_x = self.x + dx
        new_y = self.y + dy

        # Проверяем расстояние
        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        if distance <= ATTACK_RANGE:
            # Двигаться к игроку
            if self.can_move_to_position(new_x, new_y, resources, enemies, player):
                self.x = new_x
                self.y = new_y
        else:
            # Случайное движение иначе
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

            can_move = True
            for res in resources:
                if abs(new_x - res.x) < RESOURCE_SIZE and abs(new_y - res.y) < RESOURCE_SIZE:
                    can_move = False
                    break

            if can_move:
                self.x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, self.x + dx))
                self.y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, self.y + dy))

    def attack_player(self, player, dt):
        self.attack_timer += dt
        if self.attack_timer >= 2000:  # 2 секунды
            distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
            if distance <= ATTACK_RANGE:
                player.health -= self.damage
                if player.health < 0:
                    player.health = 0
                self.attack_timer = 0

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        if enemy_img:
            screen.blit(enemy_img, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, RED, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))


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
    camera_x = max(0, min(WORLD_WIDTH - SCREEN_WIDTH, player.x - SCREEN_WIDTH // 2))
    camera_y = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, player.y - SCREEN_HEIGHT // 2))
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
    player = Player()
    inventory = {'wood': 20, 'stone': 20, 'food': 0, 'meat': 0}  # Новое: добавлено 'meat' для убоины врагов
    tools = {'hand': True, 'axe': False, 'pickaxe': False, 'sword': False}
    current_tool = 'hand'
    space_cooldown = 0  # **Новое: cooldown для SPACE в мс**

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

    menu_pos = ((SCREEN_WIDTH - MENU_WIDTH) // 2, (SCREEN_HEIGHT - MENU_HEIGHT) // 2)  # Центр экрана

    last_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dt = current_time - last_time
        last_time = current_time
        if space_cooldown > 0:
            space_cooldown -= dt

        # ИСПРАВЛЕННАЯ ОТРИСОВКА ФОНА
        # Очистка экрана
        screen.fill(GRASS_GREEN)

        # Расчет правильных границ для отрисовки тайлов
        start_x = camera_x // TILE_SIZE
        start_y = camera_y // TILE_SIZE
        end_x = (camera_x + SCREEN_WIDTH) // TILE_SIZE + 1
        end_y = (camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1

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
                    variant = random.choice(grass_tiles)

                    if variant:
                        screen.blit(variant, (draw_x, draw_y))
                    else:
                        pygame.draw.rect(screen, GRASS_GREEN, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

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

        # Обновление движения животных перед player.move
        for animal in animals:
            animal.move(resources)

        # Обновление движения и атаки врагов
        for enemy in enemies:
            enemy.move_towards_player(player.x, player.y, resources, enemies, player)
            enemy.attack_player(player, dt)

        player.move(keys)

        camera_x, camera_y = update_camera(player, camera_x, camera_y)

        # Gathering logic для ресурсов (обновлено: проверка cooldown и устранение wait)
        for res in resources[:]:
            player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
            res_rect = pygame.Rect(res.x, res.y, RESOURCE_SIZE, RESOURCE_SIZE)
            if player_rect.colliderect(res_rect) and keys[pygame.K_SPACE] and space_cooldown <= 0:
                if res.take_damage(current_tool):
                    if res.type == 'tree':
                        inventory['wood'] += 1
                    elif res.type == 'rock':
                        inventory['stone'] += 1
                    resources.remove(res)
                    new_res = spawn_resource(resources)
                    resources.append(new_res)
                    print(f"Собрано {res.type}! Новый ресурс заспавнен с проверкой расстояния!")
                # **Удалено: pygame.time.wait(200)**
                space_cooldown = 200  # **Новое: устанавливаем 1-секундный cooldown**

        # Gathering logic для животных (обновлено аналогично)
        for animal in animals[:]:
            player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
            animal_rect = pygame.Rect(animal.x, animal.y, PLAYER_SIZE, PLAYER_SIZE)
            if player_rect.colliderect(animal_rect) and keys[pygame.K_SPACE] and space_cooldown <= 0:
                damage = 5 if current_tool == 'sword' else 1
                animal.hp -= damage
                if animal.hp <= 0:
                    inventory['food'] += 1
                    animals.remove(animal)
                    new_animal = spawn_animal(resources + animals, animal_types)
                    animals.append(new_animal)
                    print(f"{animal.type} убито! Food +1")
                    # **Удалено: pygame.time.wait(200)**
                space_cooldown = 200  # **Новое: 1-секундный cooldown**

        # Gathering logic для врагов (обновлено аналогично)
        for enemy in enemies[:]:
            player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
            enemy_rect = pygame.Rect(enemy.x, enemy.y, PLAYER_SIZE, PLAYER_SIZE)
            if player_rect.colliderect(enemy_rect) and keys[pygame.K_SPACE] and space_cooldown <= 0:
                damage = 5 if current_tool == 'sword' else 2
                enemy.hp -= damage
                if enemy.hp <= 0:
                    inventory['meat'] += 1
                    enemies.remove(enemy)
                    new_enemy = spawn_enemy(resources + animals + enemies)
                    enemies.append(new_enemy)
                    print("Враг убит! Meat +1")
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

        # UI (только если меню закрыты)
        if not inventory_open and not craft_open:
            tool_text = f"Инструмент: {current_tool}"
            screen.blit(font.render(tool_text, True, BLACK), (10, 10))
            health_text = f"Здоровье: {player.health}"
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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()