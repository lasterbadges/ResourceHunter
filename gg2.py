import pygame
import sys
import random
import os
import json
import math

from healthbar import HealthBar
from day_night import DayNightCycle
from enemy import Enemy
from boss import Boss, Fireball
from animal import Animal, animal_types
from Mops import Mops, mops_type
from player import Player, PushbackWave, Lightning
from resource import Resource
from building_system import Building
from sprite_manager import load_image
from sound_manager import sound_manager
from toolbar import Toolbar
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

# Инициализация экрана и шрифта
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Survival Game")
font = pygame.font.SysFont(None, 24)
# Set up the screen
clock = pygame.time.Clock()

# Загрузка текстур фона (3 ваших текстурки, assummed names: grass_tile1.png, grass_tile2.png, grass_tile3.png)
grass_tiles = [
    load_image("grass_tile1.png", (TILE_SIZE, TILE_SIZE)),
    load_image("grass_tile2.png", (TILE_SIZE, TILE_SIZE)),
    load_image("grass_tile3.png", (TILE_SIZE, TILE_SIZE))
]
# Удалить None если не загружено, или fallback
grass_tiles = [tile for tile in grass_tiles if tile]

cooldown_sprites = {'4': load_image('cooldown_4.png', size=(64, 32)), '3': load_image('cooldown_3.png', size=(64, 32)),
                    '2': load_image('cooldown_2.png', size=(64, 32)), '1': load_image('cooldown_1.png', size=(64, 32)),
                    'ready': load_image('cooldown_ready.png', size=(64, 32))}

# Функции сохранения и загрузки
def save_game(player, inventory, tools, current_tool):
    data = {
        'player_x': player.x,
        'player_y': player.y,
        'player_hp': player.hp,
        'inventory': inventory,
        'tools': tools,
        'current_tool': current_tool,
        'pushback_cooldown': player.pushback_cooldown
    }
    with open('save.json', 'w') as f:
        json.dump(data, f)
    print("Game saved.")


def load_game():
    try:
        with open('save.json', 'r') as f:
            data = json.load(f)
        print("Save data loaded successfully:", data)
        return data
    except FileNotFoundError:
        print("Save file not found, starting new game.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error loading save file: {e}, starting new game.")
        return None


button_width = 376
button_height = 103
button_x = screen_width // 2 - button_width // 2


def draw_menu(player, resources, animals, mops, enemies, camera_x, camera_y):
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
    for mops_obj in mops:
        mops_obj.draw(screen, camera_x, camera_y)
    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y)
    player.draw(screen, camera_x, camera_y)

    # Добавляем полупрозрачный оверлей для лучшей читаемости меню
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Полупрозрачный черный
    screen.blit(overlay, (0, 0))

    # Заголовок игры
    title_text = load_image("logo2.png", None)
    if title_text:
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 300))
    else:
        fallback_text = font.render("Survival Game", True, WHITE)
        screen.blit(fallback_text, (screen_width // 2 - fallback_text.get_width() // 2, screen_height // 2 - 300))

    # Кнопки меню
    def ButtonMenuDrawer(name: str, Num: int = 0):
        start_button = pygame.Rect(button_x, screen_height // 3 + 105 * Num, button_width, button_height)
        start_button_image = load_image(name, None)
        screen.blit(start_button_image, start_button)

    # Start Game button
    ButtonMenuDrawer("Play.png")

    # Settings button
    ButtonMenuDrawer("Settings.png", 1)

    # Quit button
    ButtonMenuDrawer("Exit.png", 2)


def handle_menu_events(events):
    global game_state, previous_state
    start_button = pygame.Rect(button_x, screen_height // 3 + 105 * 0, button_width, button_height)
    settings_button = pygame.Rect(button_x, screen_height // 3 + 105 * 1, button_width, button_height)
    quit_button = pygame.Rect(button_x, screen_height // 3 + 105 * 2, button_width, button_height)

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
    screen.blit(title, (screen_width // 2 - 50, screen_height // 2 - 150))
    # Кнопки разрешений
    res1_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 100, 200, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, res1_button)
    res1_text = font.render("800x800", True, BLACK)
    screen.blit(res1_text, (res1_button.x + 50, res1_button.y + 15))

    res2_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 30, 200, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, res2_button)
    res2_text = font.render("1024x768", True, BLACK)
    screen.blit(res2_text, (res2_button.x + 40, res2_button.y + 15))

    res3_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 40, 200, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, res3_button)
    res3_text = font.render("1280x720", True, BLACK)
    screen.blit(res3_text, (res3_button.x + 40, res3_button.y + 15))

    back_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 110, 200, 50)
    pygame.draw.rect(screen, RED, back_button)
    back_text = font.render("Back", True, BLACK)
    screen.blit(back_text, (back_button.x + 70, back_button.y + 15))


def handle_settings_events(events):
    global game_state, previous_state, screen_width, screen_height, screen
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            res1_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 100, 200, 50)
            res2_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 30, 200, 50)
            res3_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 40, 200, 50)
            back_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 110, 200, 50)
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
    screen.blit(resume_text, (resume_button.x + (button_width - resume_text.get_width()) // 2,
                              resume_button.y + (button_height - resume_text.get_height()) // 2))

    # Settings button
    settings_button = pygame.Rect(button_x, screen_height // 2 + 20, button_width, button_height)
    pygame.draw.rect(screen, LIGHT_GRAY, settings_button)
    settings_text = font.render("Settings", True, BLACK)
    screen.blit(settings_text, (settings_button.x + (button_width - settings_text.get_width()) // 2,
                                settings_button.y + (button_height - settings_text.get_height()) // 2))

    # Quit to Menu button
    quit_menu_button = pygame.Rect(button_x, screen_height // 2 + 90, button_width, button_height)
    pygame.draw.rect(screen, RED, quit_menu_button)
    quit_menu_text = font.render("Quit to Menu", True, BLACK)
    screen.blit(quit_menu_text, (quit_menu_button.x + (button_width - quit_menu_text.get_width()) // 2,
                                 quit_menu_button.y + (button_height - quit_menu_text.get_height()) // 2))


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
                sound_manager.stop_music()  # Останавливаем музыку
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
    screen.blit(respawn_text, (respawn_button.x + (button_width - respawn_text.get_width()) // 2,
                               respawn_button.y + (button_height - respawn_text.get_height()) // 2))

    quit_button = pygame.Rect(button_x, screen_height // 2 + 20, button_width, button_height)
    pygame.draw.rect(screen, RED, quit_button)
    quit_text = font.render("Quit to Menu", True, BLACK)
    screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2,
                            quit_button.y + (button_height - quit_text.get_height()) // 2))


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
                # Respawn: сброс hp, mana, позиция, инвентарь, инструменты
                player.hp = 100
                player.mana = 100  # Восстановление маны при респавне
                player.hunger_timer = 0
                player.x = WORLD_WIDTH // 2
                player.y = WORLD_HEIGHT // 2
                inventory = {'wood': 0, 'stone': 0, 'food': 0, 'meat': 0, 'workbench': 0, 'tent': 0, 'trap': 0,
                             'campfire': 0, 'cooked_food': 0}
                tools = {'hand': True, 'axe': False, 'pickaxe': False, 'sword': False}
                current_tool = 'hand'
                game_state = 'game'
                sound_manager.stop_music()
                print("Respawned.")
            elif quit_button.collidepoint(mouse_pos):
                save_game(player, inventory, tools, current_tool)  # Сохранение
                game_state = 'menu'
                sound_manager.stop_music()
                print("Quit to menu.")


# Spawn resource with distance check
def spawn_resource(existing_resources):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - RESOURCE_SIZE)
        y = random.randint(0, WORLD_HEIGHT - RESOURCE_SIZE)
        type_ = random.choice(['tree', 'rock'])
        candidate = Resource(x, y, type_, screen)
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
    return Resource(x, y, type_, screen)


# Spawn animal with distance check (обновлено для type)
def spawn_animal(existing_objects, animal_types):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
        y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
        animal_type = random.choice(animal_types)
        candidate = Animal(x, y, animal_type, screen)
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

# Spawn mops with distance check (обновлено для type)
def spawn_mops(existing_objects, mops_type):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - PLAYER_SIZE)
        y = random.randint(0, WORLD_HEIGHT - PLAYER_SIZE)
        mops_type = random.choice(mops_type)
        candidate = Mops(x, y, mops_type, screen)
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
    mops_type = random.choice(mops_type)
    return Mops(x, y, mops_type)

# Spawn enemy (аналогично)
def spawn_enemy(existing_objects, day_night_cycle=None):
    if day_night_cycle and day_night_cycle.is_day():
        return None
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


# Spawn boss
def spawn_boss(existing_objects):
    attempts = 100
    for _ in range(attempts):
        x = random.randint(0, WORLD_WIDTH - BOSS_SIZE)
        y = random.randint(0, WORLD_HEIGHT - BOSS_SIZE)
        candidate = Boss(x, y)
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
    x = random.randint(0, WORLD_WIDTH - BOSS_SIZE)
    y = random.randint(0, WORLD_HEIGHT - BOSS_SIZE)
    return Boss(x, y)


def update_camera(player, camera_x, camera_y):
    camera_x = max(0, min(WORLD_WIDTH - screen_width, player.x - screen_width // 2))
    camera_y = max(0, min(WORLD_HEIGHT - screen_height, player.y - screen_height // 2))
    return camera_x, camera_y


# Функция для рисования меню инвентаря (обновлено: добавлен Meat)
def draw_inventory_menu(screen, inventory, menu_pos):
    # Полупрозрачный фон
    menu_surf = pygame.Surface((MENU_WIDTH, MENU_HEIGHT + 100), pygame.SRCALPHA)
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
    screen.blit(font.render(f"Мясо: {inventory['meat']}", True, WHITE), (menu_pos[0] + 10, inv_y + 90))
    screen.blit(font.render(f"Приготовленная еда: {inventory.get('cooked_food', 0)}", True, WHITE),
                (menu_pos[0] + 10, inv_y + 120))
    screen.blit(font.render(f"Верстак: {inventory.get('workbench', 0)}", True, WHITE), (menu_pos[0] + 10, inv_y + 150))
    screen.blit(font.render(f"Палатка: {inventory.get('tent', 0)}", True, WHITE), (menu_pos[0] + 10, inv_y + 180))
    screen.blit(font.render(f"Капкан: {inventory.get('trap', 0)}", True, WHITE), (menu_pos[0] + 10, inv_y + 210))
    screen.blit(font.render(f"Костер: {inventory.get('campfire', 0)}", True, WHITE), (menu_pos[0] + 10, inv_y + 240))


# Функция для рисования меню крафта (обновлено для меча и верстака)
def draw_craft_menu(screen, inventory, tools, menu_pos):
    # Полупрозрачный фон
    menu_surf = pygame.Surface((MENU_WIDTH, MENU_HEIGHT + 50), pygame.SRCALPHA)
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

    # Меч
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
        button_y += BUTTON_HEIGHT + 10
    else:
        screen.blit(font.render("Меч: ✓", True, GREEN), (menu_pos[0] + 10, button_y))
        button_y += 30

    # Верстак
    wb_req = "5 дерева"
    can_craft_wb = inventory['wood'] >= 5
    button_color = GREEN if can_craft_wb else GRAY
    wb_text = font.render("Скрафтить", True, WHITE)
    wb_button = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, button_color, wb_button)
    screen.blit(font.render("Верстак:", True, WHITE), (menu_pos[0] + 10, button_y - 20))
    screen.blit(font.render(wb_req, True, WHITE), (menu_pos[0] + 80, button_y - 20))
    screen.blit(wb_text, (wb_button.x + 10, wb_button.y + 10))
    buttons.append(('workbench', wb_button, can_craft_wb))

    return buttons


# --- МЕНЮ ВЕРСТАКА ---
def draw_workbench_menu(screen, inventory, menu_pos):
    # Полупрозрачный фон
    menu_surf = pygame.Surface((MENU_WIDTH, MENU_HEIGHT + 100), pygame.SRCALPHA)
    menu_surf.fill(SEMI_BLACK)
    screen.blit(menu_surf, menu_pos)

    title = font.render("Верстак", True, WHITE)
    screen.blit(title, (menu_pos[0] + 10, menu_pos[1] + 10))

    button_y = menu_pos[1] + 50
    buttons = []

    # Палатка
    req = "10 дерева, 2 камня"
    can_craft = inventory['wood'] >= 10 and inventory['stone'] >= 2
    button_color = GREEN if can_craft else GRAY
    btn_rect = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, button_color, btn_rect)
    screen.blit(font.render("Палатка", True, WHITE), (menu_pos[0] + 10, button_y - 20))
    screen.blit(font.render(req, True, WHITE), (menu_pos[0] + 100, button_y - 20))
    screen.blit(font.render("Скрафтить", True, WHITE), (btn_rect.x + 10, btn_rect.y + 10))
    buttons.append(('tent', btn_rect, can_craft))
    button_y += BUTTON_HEIGHT + 30

    # Капкан
    req = "7 дерева, 3 камня"
    can_craft = inventory['wood'] >= 7 and inventory['stone'] >= 3
    button_color = GREEN if can_craft else GRAY
    btn_rect = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, button_color, btn_rect)
    screen.blit(font.render("Капкан", True, WHITE), (menu_pos[0] + 10, button_y - 20))
    screen.blit(font.render(req, True, WHITE), (menu_pos[0] + 100, button_y - 20))
    screen.blit(font.render("Скрафтить", True, WHITE), (btn_rect.x + 10, btn_rect.y + 10))
    buttons.append(('trap', btn_rect, can_craft))
    button_y += BUTTON_HEIGHT + 30

    # Костер
    req = "5 дерева, 5 камней"
    can_craft = inventory['wood'] >= 5 and inventory['stone'] >= 5
    button_color = GREEN if can_craft else GRAY
    btn_rect = pygame.Rect(menu_pos[0] + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, button_color, btn_rect)
    screen.blit(font.render("Костер", True, WHITE), (menu_pos[0] + 10, button_y - 20))
    screen.blit(font.render(req, True, WHITE), (menu_pos[0] + 100, button_y - 20))
    screen.blit(font.render("Скрафтить", True, WHITE), (btn_rect.x + 10, btn_rect.y + 10))
    buttons.append(('campfire', btn_rect, can_craft))

    return buttons


def handle_workbench_craft(item_name, inventory):
    if item_name == 'tent' and inventory['wood'] >= 10 and inventory['stone'] >= 2:
        inventory['wood'] -= 10
        inventory['stone'] -= 2
        inventory['tent'] = inventory.get('tent', 0) + 1
        print("Палатка скрафчена!")
    elif item_name == 'trap' and inventory['wood'] >= 7 and inventory['stone'] >= 3:
        inventory['wood'] -= 7
        inventory['stone'] -= 3
        inventory['trap'] = inventory.get('trap', 0) + 1
        print("Капкан скрафчен!")
    elif item_name == 'campfire' and inventory['wood'] >= 5 and inventory['stone'] >= 5:
        inventory['wood'] -= 5
        inventory['stone'] -= 5
        inventory['campfire'] = inventory.get('campfire', 0) + 1
        print("Костер скрафчен!")


# Функция для обработки крафта (обновлено)
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
    elif tool_name == 'workbench' and inventory['wood'] >= 5:
        inventory['wood'] -= 5
        inventory['workbench'] = inventory.get('workbench', 0) + 1
        print("Верстак скрафчен! 🛠️")
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

    player = Player(screen)
    game_state = 'menu'
    previous_state = None
    inventory = {'wood': 0, 'stone': 0, 'food': 0, 'meat': 0, 'workbench': 0, 'tent': 0, 'trap': 0, 'campfire': 0,
                 'cooked_food': 0}
    tools = {'hand': True, 'axe': False, 'pickaxe': False, 'sword': False}
    current_tool = 'hand'
    space_cooldown = 0  # **Новое: cooldown для SPACE в мс**
    lightning_cooldown = 0  # Cooldown для молнии
    lightnings = []  # Список молний
    pushback_waves = []  # Визуальные эффекты отталкивания
    food_cooldown = 0  # Cooldown для еды
    meat_cooldown = 0  # Cooldown для мяса
    day_night_cycle = DayNightCycle()  # Система дня и ночи

    buildings = []  # Список построек
    workbench_menu_open = False
    building_mode = False
    build_options = ['workbench', 'tent', 'trap', 'campfire']
    current_build_index = 0
    active_menu = None  # Переменная для отслеживания активного меню

    def set_active_menu(menu):
        global active_menu, inventory_open, craft_open, workbench_menu_open, building_mode
        if active_menu == menu:
            # close it
            if menu == 'inventory':
                inventory_open = False
            elif menu == 'craft':
                craft_open = False
            elif menu == 'workbench':
                workbench_menu_open = False
            elif menu == 'building':
                building_mode = False
            active_menu = None
        else:
            # close current
            if active_menu == 'inventory':
                inventory_open = False
            elif active_menu == 'craft':
                craft_open = False
            elif active_menu == 'workbench':
                workbench_menu_open = False
            elif active_menu == 'building':
                building_mode = False
            # open new
            if menu == 'inventory':
                inventory_open = True
            elif menu == 'craft':
                craft_open = True
            elif menu == 'workbench':
                workbench_menu_open = True
            elif menu == 'building':
                building_mode = True
            active_menu = menu

    menu_camera_x = 0
    menu_camera_y = 0
    menu_player = Player(screen)  # Специальный игрок для меню
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

    menu_mops = []
    for _ in range(5):
        new_mops = spawn_mops(menu_resources + menu_animals + menu_mops, mops_type)
        menu_mops.append(new_mops)

    menu_enemies = []
    for _ in range(5):
        new_enemy = spawn_enemy(menu_resources + menu_animals + menu_mops + menu_enemies)
        menu_enemies.append(new_enemy)

    # Инициализируем камеру меню
    menu_camera_x, menu_camera_y = update_camera(menu_player, menu_camera_x, menu_camera_y)

    # pygame.mixer.music.load("background_music.mp3")
    # pygame.mixer.music.play(0)

    # Загрузка сохранения
    save_data = load_game()
    if save_data:
        print("Applying save data...")
        player.x = save_data.get('player_x', player.x)
        player.y = save_data.get('player_y', player.y)
        player.hp = save_data.get('player_hp', player.hp)
        inventory.update(save_data.get('inventory', {}))
        tools.update(save_data.get('tools', {}))
        current_tool = save_data.get('current_tool', current_tool)
        player.pushback_cooldown = save_data.get('pushback_cooldown', 0)
        print(f"Loaded player position: {player.x}, {player.y}, HP: {player.hp}")
        print(f"Loaded inventory: {inventory}")
        print(f"Loaded tools: {tools}")
        print(f"Loaded current tool: {current_tool}")

    # Спавн ресурсов с проверкой расстояния
    resources = []
    for _ in range(40):
        new_res = spawn_resource(resources)
        resources.append(new_res)

    # Спавн животных с проверкой расстояния (новые виды)
    animals = []
    for _ in range(10):  # 10 животных
        new_animal = spawn_animal(resources + animals, animal_types)
        animals.append(new_animal)

    # Спавн мопсов с проверкой расстояния
    mops = []
    for _ in range(5):  # 5 мопсов
        new_mops = spawn_mops(resources + animals + mops, mops_type)
        mops.append(new_mops)

    # Спавн врагов
    enemies = []
    for _ in range(5):
        new_enemy = spawn_enemy(resources + animals + mops + enemies, day_night_cycle)
        if new_enemy:
            enemies.append(new_enemy)

    # Спавн босса
    bosses = []
    new_boss = spawn_boss(resources + animals + mops + enemies + bosses)
    if new_boss:
        bosses.append(new_boss)
        print("Босс появился в мире!")

    camera_x = 0
    camera_y = 0
    inventory_open = False  # Флаг меню инвентаря
    craft_open = False  # Флаг меню крафта
    fireballs = []  # Список огненных шаров

    menu_pos = ((screen_width - MENU_WIDTH) // 2, (screen_height - MENU_HEIGHT) // 2)  # Центр экрана

    last_time = pygame.time.get_ticks()
    MAX_HP = 100
    BAR_WIDTH = 300
    BAR_HEIGHT = 100
    BAR_X = 0
    BAR_Y = 100

    # --- Image Loading Setup ---
    loaded_fill_img = None
    loaded_frame_img = None

    try:
        # Attempt to load and scale the images
        loaded_fill_img = load_image('progressbar1.png', (BAR_WIDTH, BAR_HEIGHT))
        loaded_frame_img = load_image('progressbar2.png', (BAR_WIDTH, BAR_HEIGHT))

        print("Изображения полосы здоровья успешно загружены.")
    except pygame.error as e:
        print(f"Ошибка загрузки изображений полосы здоровья: {e}")
        print("Используется цветная прямоугольная полоса.")
    except FileNotFoundError:
        print("Ошибка: Файлы изображений не найдены. Используется цветная полоса.")

    # --- HealthBar Instance Creation ---
    player_health_bar = HealthBar(
        BAR_X,
        BAR_Y,
        BAR_WIDTH,
        BAR_HEIGHT,
        MAX_HP,
        loaded_fill_img,
        loaded_frame_img
    )

    # --- Toolbar Instance Creation ---
    toolbar = Toolbar(screen_width, screen_height, font)

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
                save_game(player, inventory, tools, current_tool)
                running = False

        # Обработка событий в зависимости от состояния
        if game_state == 'menu':
            handle_menu_events(events)
            move_speed = 1  # Увеличим скорость для более очевидного движения
            menu_player.x += move_speed * f

            # Обновление состояния анимации (чтобы игрок не выглядел стоящим)
            menu_player.is_moving = True
            menu_player.direction = 'right' if f > 0 else 'left'
            menu_player.walk_timer += 1
            if menu_player.walk_timer >= 10:
                menu_player.walk_frame = (menu_player.walk_frame + 1) % 4
                menu_player.walk_timer = 0

            # Проверка границ и реверс направления
            if f > 0 and menu_player.x >= WORLD_WIDTH - screen_width // 2:
                f = -1  # Движение влево
            elif f < 0 and menu_player.x <= screen_width // 2:
                f = 1  # Движение вправо

            # 2. Обновляем движение животных
            for animal in menu_animals:
                animal.move(menu_resources)

            # 3. Обновляем движение мопсов
            for mops_obj in menu_mops:
                mops_obj.move(menu_resources)

            # 4. Обновляем движение врагов
            for enemy in menu_enemies:
                # В меню они просто бродят
                enemy.move_randomly(menu_resources, menu_enemies, menu_player)

            # 4. Обновляем камеру меню, чтобы она следовала за игроком
            menu_camera_x, menu_camera_y = update_camera(menu_player, menu_camera_x, menu_camera_y)

            # 5. Отрисовка фона меню
            draw_menu(menu_player, menu_resources, menu_animals, menu_mops, menu_enemies, menu_camera_x, menu_camera_y)
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

                # Обновление системы дня и ночи
                day_night_cycle.update()
                # Управление музыкой в зависимости от времени суток
                if day_night_cycle.is_day():
                    if sound_manager.music_playing:
                        sound_manager.stop_music()
                else:
                    # Ночь - включаем музыку только если враги начинают спавниться
                    if len(enemies) > 0 and not sound_manager.music_playing:
                        sound_manager.play_night_music()

                if day_night_cycle.is_day() == False and len(enemies) < 5:
                    for _ in range(5):
                        new_enemy = spawn_enemy(resources + animals + mops + enemies, day_night_cycle)
                        if new_enemy:
                            enemies.append(new_enemy)
                            # Включаем ночную музыку при спавне первого врага ночью
                            if not sound_manager.music_playing:
                                sound_manager.play_night_music()

                # Обновление cooldown для SPACE
                space_cooldown = max(0, space_cooldown - dt)
                lightning_cooldown = max(0, lightning_cooldown - dt)
                player.pushback_cooldown = max(0, player.pushback_cooldown - dt)
                food_cooldown = max(0, food_cooldown - dt)
                meat_cooldown = max(0, meat_cooldown - dt)

                # Система голода
                player.hunger_timer += dt
                if player.hunger_timer > 60000:  # Каждые 5 секунд
                    player.hp -= 1
                    player.hunger_timer = 0
                    if player.hp <= 0:
                        game_state = 'game_over'

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
                    if workbench_menu_open:
                        workbench_menu_open = False
                    elif building_mode:
                        building_mode = False
                    else:
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

                # РЕЖИМ СТРОИТЕЛЬСТВА
                if keys[pygame.K_b] and not inventory_open and not craft_open and not workbench_menu_open:
                    building_mode = not building_mode
                    print("Режим строительства:", "вкл" if building_mode else "выкл")
                    pygame.time.wait(200)

                # Выбор постройки в режиме строительства
                if building_mode:
                    if keys[pygame.K_1]: current_build_index = 0
                    if keys[pygame.K_2]: current_build_index = 1
                    if keys[pygame.K_3]: current_build_index = 2
                    if keys[pygame.K_4]: current_build_index = 3

                    # Размещение ЛКМ
                    if pygame.mouse.get_pressed()[0]:
                        mx, my = pygame.mouse.get_pos()
                        world_mx = mx + camera_x
                        world_my = my + camera_y
                        item_to_build = build_options[current_build_index]

                        if inventory.get(item_to_build, 0) > 0:
                            # Проверка коллизий перед постройкой
                            new_build_rect = pygame.Rect(world_mx - 30, world_my - 30, BUILDING_SIZE, BUILDING_SIZE)
                            collides = False
                            for b in buildings:
                                if new_build_rect.colliderect(
                                    pygame.Rect(b.x, b.y, BUILDING_SIZE, BUILDING_SIZE)): collides = True
                            if not collides:
                                buildings.append(Building(world_mx - 30, world_my - 30, item_to_build))
                                inventory[item_to_build] -= 1
                                sound_manager.play_sound('build')
                                pygame.time.wait(200)

                # ВЗАИМОДЕЙСТВИЕ С ПОСТРОЙКАМИ (E)
                if keys[pygame.K_e]:
                    player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
                    for b in buildings:
                        b_rect = pygame.Rect(b.x, b.y, BUILDING_SIZE, BUILDING_SIZE)
                        # Расширим зону взаимодействия
                        if player_rect.colliderect(b_rect.inflate(20, 20)):
                            if b.type == 'workbench':
                                workbench_menu_open = not workbench_menu_open
                                pygame.time.wait(200)
                            elif b.type == 'tent':
                                day_night_cycle.time = 300  # Сброс на утро
                                print("Вы поспали в палатке. Наступило утро.")
                                pygame.time.wait(500)
                            elif b.type == 'campfire':
                                if inventory['meat'] > 0:
                                    inventory['meat'] -= 1
                                    inventory['cooked_food'] = inventory.get('cooked_food', 0) + 1
                                    print("Мясо пожарено!")
                                    pygame.time.wait(200)

                # Смена инструментов (только если меню закрыты и не в режиме строительства)
                if not inventory_open and not craft_open and not workbench_menu_open and not building_mode:
                    for i in range(1, 9):
                        key = getattr(pygame, f'K_{i}')
                        if keys[key]:
                            selected = toolbar.select_slot(i - 1, inventory, tools)
                            if selected:
                                current_tool = selected
                            break

                if keys[pygame.K_f] and inventory['food'] > 0 and food_cooldown <= 0:
                    player.hp = min(100, player.hp + 20)
                    inventory['food'] -= 1
                    food_cooldown = 200

                if keys[pygame.K_m] and inventory['meat'] > 0 and meat_cooldown <= 0:
                    player.hp = min(100, player.hp + 30)
                    inventory['meat'] -= 1
                    meat_cooldown = 200

                # Восстановление маны со временем
                player.mana = min(player.max_mana, player.mana + player.mana_regen_rate * dt)

                #Обновление HPbar
                if player.hp != player_health_bar.current_hp:
                    player_health_bar.set_health(player.hp)
                # Молния (требует 20 маны)
                mana_cost = 20
                if keys[pygame.K_h] and inventory.get('cooked_food', 0) > 0 and food_cooldown <= 0:
                    player.hp = min(100, player.hp + 50)
                    inventory['cooked_food'] -= 1
                    food_cooldown = 200

                # Молния
                if keys[pygame.K_q] and lightning_cooldown <= 0:
                    closest = None
                    min_dist = 200
                    for enemy in enemies:
                        dist = ((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            closest = enemy
                    for boss in bosses:
                        dist = ((player.x - boss.x) ** 2 + (player.y - boss.y) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            closest = boss
                    for animal in animals:
                        dist = ((player.x - animal.x) ** 2 + (player.y - animal.y) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            closest = animal
                    for mops_obj in mops:
                        dist = ((player.x - mops_obj.x) ** 2 + (player.y - mops_obj.y) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            closest = mops_obj
                    if closest:
                        sound_manager.play_sound('lightning')
                        player.mana -= mana_cost  # Тратим ману
                        damage = random.randint(15, 20)
                        closest.hp -= damage
                        if closest.hp <= 0:
                            if isinstance(closest, Animal):
                                inventory['food'] += 1
                                animals.remove(closest)
                                new_animal = spawn_animal(resources + animals, animal_types)
                                animals.append(new_animal)
                            elif isinstance(closest, Mops):
                                inventory['meat'] += 1
                                mops.remove(closest)
                                new_mops = spawn_mops(resources + animals + mops, mops_type)
                                mops.append(new_mops)
                            elif isinstance(closest, Enemy):
                                inventory['meat'] += 1
                                enemies.remove(closest)
                                new_enemy = spawn_enemy(resources + animals + mops + enemies, day_night_cycle)
                                if new_enemy:
                                    enemies.append(new_enemy)
                            elif isinstance(closest, Boss):
                                bosses.remove(closest)
                        target_size = closest.size if hasattr(closest, 'size') else PLAYER_SIZE
                        lightnings.append(Lightning(player.x + PLAYER_SIZE // 2, player.y + PLAYER_SIZE // 2,
                                                    closest.x + target_size // 2, closest.y + target_size // 2))
                        lightning_cooldown = 5000  # 5 сек (уменьшил, так как теперь есть ограничение маны)

                # Отталкивание (клавиша E) - не тратит ману, перезарядка 15 сек
                if keys[pygame.K_e] and player.pushback_cooldown <= 0:
                    player.pushback(enemies, animals, mops, bosses, pushback_waves, inventory, resources, day_night_cycle)

                # Обновление движения животных перед player.move
                # ЛОГИКА КАПКАНОВ
                for animal in animals[:]:
                    animal.move(resources)
                    # Проверка капканов
                    animal_rect = pygame.Rect(animal.x, animal.y, PLAYER_SIZE, PLAYER_SIZE)
                    for b in buildings[:]:
                        if b.type == 'trap':
                            trap_rect = pygame.Rect(b.x, b.y, BUILDING_SIZE, BUILDING_SIZE)
                            if animal_rect.colliderect(trap_rect):
                                animal.hp = 0
                                inventory['food'] += 2
                                animals.remove(animal)
                                new_animal = spawn_animal(resources + animals, animal_types)
                                animals.append(new_animal)
                                buildings.remove(b)  # Капкан срабатывает и исчезает
                                print("Капкан сработал!")
                                break

                # Обновление движения мопсов
                for mops_obj in mops[:]:
                    mops_obj.move(resources)

                # Обновление движения и атаки врагов
                for enemy in enemies[:]:
                    enemy.move_towards_player(player.x, player.y, resources, enemies, player, day_night_cycle)
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        new_enemy = spawn_enemy(resources + animals + enemies, day_night_cycle)
                        if new_enemy:
                            enemies.append(new_enemy)
                    else:
                        enemy.attack_player(player, dt, player_health_bar)

                # Обновление движения и атаки боссов
                for boss in bosses[:]:
                    boss.move_towards_player(player.x, player.y, resources, enemies, player, bosses)
                    if boss.hp <= 0:
                        bosses.remove(boss)
                    else:
                        boss.attack_player(player, dt, fireballs)

                # Обновление огненных шаров
                for fireball in fireballs[:]:
                    fireball.move()
                    # Коллизия с игроком
                    if abs(fireball.x - player.x) < PLAYER_SIZE and abs(fireball.y - player.y) < PLAYER_SIZE:
                        player.hp -= 30
                        fireballs.remove(fireball)
                        continue
                    # Удалить если вышел за границы или истекло время
                    if fireball.x < 0 or fireball.x > WORLD_WIDTH or fireball.y < 0 or fireball.y > WORLD_HEIGHT or fireball.is_expired():
                        fireballs.remove(fireball)

                # Обновление молний
                for lightning in lightnings[:]:
                    lightning.update()
                    if lightning.is_expired():
                        lightnings.remove(lightning)

                # Обновление эффектов отталкивания
                for wave in pushback_waves[:]:
                    wave.update()
                    if wave.is_expired():
                        pushback_waves.remove(wave)

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
                            sound_manager.play_sound('destroying')
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
                        sound_manager.play_random_punch()
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

                # Gathering logic для мопсов
                for mops_obj in mops[:]:
                    player_rect = pygame.Rect(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE)
                    mops_rect = pygame.Rect(mops_obj.x, mops_obj.y, PLAYER_SIZE, PLAYER_SIZE)
                    if player_rect.colliderect(mops_rect) and keys[pygame.K_SPACE] and space_cooldown <= 0:
                        print(f"DEBUG: Colliding with mops at ({mops_obj.x}, {mops_obj.y}), type: {mops_obj.type}")
                        sound_manager.play_random_punch()
                        damage = 5 if current_tool == 'sword' else 1
                        mops_obj.hp -= damage
                        if mops_obj.hp <= 0:
                            inventory['meat'] += 1
                            mops.remove(mops_obj)
                            new_mops = spawn_mops(resources + animals + mops, mops_type)
                            mops.append(new_mops)
                            print(f"DEBUG: Mops убит! Meat +1")
                            # **Удалено: pygame.time.wait(200)**
                        space_cooldown = 200  # **Новое: 1-секундный cooldown**

                # Gathering logic для врагов (обновлено аналогично)
                for enemy in enemies[:]:
                    distance = ((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2) ** 0.5
                    if distance <= ATTACK_RANGE and keys[pygame.K_SPACE] and space_cooldown <= 0:
                        print(f"DEBUG: Attacking enemy at ({enemy.x}, {enemy.y}), distance: {distance}")
                        sound_manager.play_random_punch()
                        damage = 5 if current_tool == 'sword' else 2
                        enemy.hp -= damage
                        if enemy.hp <= 0:
                            inventory['meat'] += 1
                            enemies.remove(enemy)
                            new_enemy = spawn_enemy(resources + animals + enemies, day_night_cycle)
                            if new_enemy:
                                enemies.append(new_enemy)
                            print("DEBUG: Враг убит! Meat +1")
                            # **Удалено: pygame.time.wait(200)**
                        space_cooldown = 200  # **Новое: 1-секундный cooldown**

                # Gathering logic для боссов
                for boss in bosses[:]:
                    distance = ((player.x - boss.x) ** 2 + (player.y - boss.y) ** 2) ** 0.5
                    if distance <= boss.size and keys[pygame.K_SPACE] and space_cooldown <= 0:
                        sound_manager.play_random_punch()
                        damage = 5 if current_tool == 'sword' else 2
                        boss.hp -= damage
                        if boss.hp <= 0:
                            bosses.remove(boss)
                        space_cooldown = 200

                # Рисуем мир
                for res in resources:
                    res.draw(screen, camera_x, camera_y)
                for animal in animals:
                    animal.draw(screen, camera_x, camera_y)  # Добавлено рисование животных
                for mops_obj in mops:
                    mops_obj.draw(screen, camera_x, camera_y)  # Рисуем мопсов
                for enemy in enemies:
                    enemy.draw(screen, camera_x, camera_y)  # Рисуем врагов
                for boss in bosses:
                    boss.draw(screen, camera_x, camera_y, player)
                for b in buildings:
                    b.draw(screen, camera_x, camera_y)
                for fireball in fireballs:
                    fireball.draw(screen, camera_x, camera_y)
                for lightning in lightnings:
                    lightning.draw(screen, camera_x, camera_y)
                for wave in pushback_waves:
                    wave.draw(screen, camera_x, camera_y)

                player.draw(screen, camera_x, camera_y)

                # Рисуем призрак постройки
                if building_mode:
                    mx, my = pygame.mouse.get_pos()
                    item_name = build_options[current_build_index]
                    txt = font.render(f"Размещение: {item_name} (Имеется: {inventory.get(item_name, 0)})", True, WHITE)
                    screen.blit(txt, (mx + 20, my - 20))
                    pygame.draw.rect(screen, (255, 255, 255), (mx, my, BUILDING_SIZE, BUILDING_SIZE), 2)

                # Оверлей для плавного перехода дня и ночи с растушевкой
                light_intensity = day_night_cycle.get_light_intensity()
                if light_intensity < 1:  # Рисовать оверлей только если не полный день
                    darkness = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                    darkness.fill((0, 0, 0, 240 - 240 * light_intensity))

                    def create_circle_mask(radius):
                        size = radius * 2
                        mask = pygame.Surface((size, size), pygame.SRCALPHA)
                        for r in range(radius, 0, -1):
                            alpha = 240 - int(240 * (r / radius))
                            pygame.draw.circle(mask, (255, 128, 128, alpha), (radius, radius), r)
                        return mask

                    small_mask = create_circle_mask(150)

                    # Свет вокруг игрока
                    current_mask = small_mask
                    darkness.blit(current_mask, (player.x + PLAYER_SIZE // 2 - camera_x - current_mask.get_width() // 2,
                                                 player.y + PLAYER_SIZE // 2 - camera_y - current_mask.get_height() // 2),
                                  special_flags=pygame.BLEND_RGBA_SUB)

                    # Свет вокруг костров
                    fire_mask = create_circle_mask(200)
                    for b in buildings:
                        if b.type == 'campfire':
                            draw_x = b.x + BUILDING_SIZE // 2 - camera_x
                            draw_y = b.y + BUILDING_SIZE // 2 - camera_y
                            darkness.blit(fire_mask,
                                          (draw_x - fire_mask.get_width() // 2, draw_y - fire_mask.get_height() // 2),
                                          special_flags=pygame.BLEND_RGBA_SUB)

                    screen.blit(darkness, (0, 0))

                # Рисуем тулбар, если не в режиме строительства
                if not building_mode:
                    toolbar.draw(screen, inventory, tools, current_tool)

                # Визуальный таймер cooldown кувырка
                key = str((player.roll_cooldown + 59) // 60) if player.roll_cooldown > 0 else 'ready'
                screen.blit(cooldown_sprites[key], (screen_width - 100, 50))

                # UI (только если меню закрыты)
                if not inventory_open and not craft_open and not workbench_menu_open:
                    pos_text = f"Позиция: ({player.x}, {player.y})"
                    
                    # Показываем cooldown отталкивания
                    if player.pushback_cooldown > 0:
                        pushback_cd_text = f"Отталкивание: {int(player.pushback_cooldown / 1000)}с"
                        screen.blit(font.render(pushback_cd_text, True, (150, 75, 0)), (10, 185))
                    else:
                        screen.blit(font.render("Отталкивание: готово", True, (0, 150, 0)), (10, 185))
                    
                    screen.blit(font.render(pos_text, True, BLACK), (10, 100))

                    player_health_bar.draw(screen)

                    # Полоска маны под полоской здоровья
                    mana_bar_width = 150
                    mana_bar_height = 15
                    mana_bar_x = BAR_X + 75  # Смещение для центрирования под healthbar
                    mana_bar_y = BAR_Y + BAR_HEIGHT + 5
                    # Фон полоски маны
                    pygame.draw.rect(screen, (50, 50, 100), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
                    # Заполнение полоски маны
                    mana_fill_width = int((player.mana / player.max_mana) * mana_bar_width)
                    pygame.draw.rect(screen, (0, 100, 255), (mana_bar_x, mana_bar_y, mana_fill_width, mana_bar_height))
                    # Рамка полоски маны
                    pygame.draw.rect(screen, (0, 0, 150), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 2)

                # Рисуем меню инвентаря (если открыто)
                if inventory_open:
                    draw_inventory_menu(screen, inventory, menu_pos)
                    close_text = font.render("Нажми I для закрытия", True, WHITE)
                    screen.blit(close_text, (menu_pos[0] + 10, menu_pos[1] + MENU_HEIGHT + 70))

                # Рисуем меню крафта (если открыто)
                if craft_open:
                    buttons = draw_craft_menu(screen, inventory, tools, menu_pos)
                    if pygame.mouse.get_pressed()[0]:
                        mouse_pos = pygame.mouse.get_pos()
                        for tool_name, button_rect, can_craft in buttons:
                            if button_rect.collidepoint(mouse_pos) and can_craft:
                                handle_craft(tool_name, inventory, tools)
                                pygame.time.wait(200)
                                break
                    close_text = font.render("Нажми C для закрытия", True, WHITE)
                    screen.blit(close_text, (menu_pos[0] + 10, menu_pos[1] + MENU_HEIGHT - 30))

                # Рисуем меню верстака (если открыто)
                if workbench_menu_open:
                    wb_buttons = draw_workbench_menu(screen, inventory, menu_pos)
                    if pygame.mouse.get_pressed()[0]:
                        mouse_pos = pygame.mouse.get_pos()
                        for item_name, btn_rect, can_craft in wb_buttons:
                            if btn_rect.collidepoint(mouse_pos) and can_craft:
                                handle_workbench_craft(item_name, inventory)
                                pygame.time.wait(200)
                                break
                    close_text = font.render("Нажми E или ESC для закрытия", True, WHITE)
                    screen.blit(close_text, (menu_pos[0] + 10, menu_pos[1] + MENU_HEIGHT + 70))

            except Exception as e:
                print(f"Error in game: {e}")
        elif game_state == 'settings':
            draw_settings()
        elif game_state == 'pause':
            draw_pause()
        elif game_state == 'game_over':
            draw_game_over()
            player_health_bar.set_health(100)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()