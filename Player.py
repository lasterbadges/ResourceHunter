import pygame
class Player:
    def __init__(self, WORLD_WIDTH, WORLD_HEIGHT):
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        self.speed = 5
        self.health = 100
        self.direction = 'down'
        self.is_moving = False
        self.walk_timer = 0
        self.walk_frame = 0

    def move(self, keys):
        prev_x, prev_y = self.x, self.y
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = 'left'
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = 'right'
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = 'up'
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = 'down'
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
            text = font.render(self.direction, True, BLACK)
            screen.blit(text, (draw_x + 5, draw_y + 5))
