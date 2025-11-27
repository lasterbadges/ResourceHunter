import pygame


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Fallback colors for when images are not found
RED_FALLBACK = (255, 0, 0)
GREEN_FALLBACK = (0, 255, 0)
ORANGE_FALLBACK = (255, 165, 0)


# --- Class HealthBar ---
class HealthBar:

    def __init__(self, x, y, width, height, max_hp, fill_img=None, frame_img=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.current_hp = max_hp

        # Images for the bar
        self.fill_img = fill_img
        self.frame_img = frame_img
        self.use_images = fill_img is not None and frame_img is not None
        # Rectangles for fallback or drawing HP text
        self.frame_rect = pygame.Rect(x, y, width, height)

    def set_health(self, amount):
        """Устанавливает текущее здоровье, с учетом ограничений (0 до max_hp)."""
        self.current_hp = max(0, min(amount, self.max_hp))

    def take_damage(self, amount):
        """Уменьшает текущее здоровье."""
        self.set_health(self.current_hp - amount)
        return self.current_hp

    def heal(self, amount):
        """Увеличивает текущее здоровье."""
        self.set_health(self.current_hp + amount)
        return self.current_hp

    def draw(self, surface):
        """Рисует полосу здоровья на заданной поверхности."""

        # 1. Calculate the health ratio
        health_ratio = self.current_hp / self.max_hp
        fill_width = int(self.width * health_ratio)

        if self.use_images:
            # --- Image-based Health Bar ---

            # Draw the frame/background image (full width)
            surface.blit(self.frame_img, (self.x, self.y))

            # Crop and draw the health fill image
            if fill_width > 0:
                # Create a subsurface (cropped image) based on current fill_width
                fill_rect = pygame.Rect(0, 0, fill_width, self.height)
                health_fill_surface = self.fill_img.subsurface(fill_rect)

                # Blit the cropped fill surface over the frame
                surface.blit(health_fill_surface, (self.x, self.y))

        else:
            # --- Colored Rectangle Health Bar (Fallback) ---

            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)

            # Dynamic color change based on health ratio
            if health_ratio > 0.5:
                color = GREEN_FALLBACK
            elif health_ratio > 0.2:
                color = ORANGE_FALLBACK
            else:
                color = RED_FALLBACK

            # Draw the health fill
            pygame.draw.rect(surface, color, fill_rect)

            # Draw the frame (e.g., black border)
            pygame.draw.rect(surface, BLACK, self.frame_rect, 3)

            # Draw numerical health text over the bar
        #hp_text = self.font.render(f"{self.current_hp}/{self.max_hp}", True, BLACK)
        #text_rect = hp_text.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        #surface.blit(hp_text, text_rect)