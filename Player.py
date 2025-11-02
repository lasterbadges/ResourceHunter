import  pygame
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PLAYER_SIZE = 40
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000

class Player:
    def __init__(self, font, player_sprites):
        self.player_sprites = player_sprites
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
            sprite = self.player_sprites[self.direction]['walk'][self.walk_frame]
        else:
            sprite = self.player_sprites[self.direction]['stand']

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, GREEN, (draw_x, draw_y, PLAYER_SIZE, PLAYER_SIZE))
            text = self.font.render(self.direction, True, BLACK)
            screen.blit(text, (draw_x + 5, draw_y + 5))

