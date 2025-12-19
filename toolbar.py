import pygame

class Toolbar:
    def __init__(self, screen_width, screen_height, font):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.bar_height = 60
        self.bar_color = (139, 69, 19)  # Коричневый
        self.slot_width = 80
        self.slot_height = 50
        self.gap = 10  # Промежуток между слотами
        self.slots = [
            ('pickaxe', 'Кирка'),
            ('sword', 'Меч'),
            ('axe', 'Топор'),
            ('food', 'Еда')
        ]
        self.current_index = 0  # Индекс выбранного слота

    def draw(self, screen, inventory, tools, current_tool):
        # Рисуем слоты
        total_width = len(self.slots) * self.slot_width + (len(self.slots) - 1) * self.gap
        start_x = (self.screen_width - total_width) // 2
        for i, (item, label) in enumerate(self.slots):
            slot_x = start_x + i * (self.slot_width + self.gap)
            slot_rect = pygame.Rect(slot_x, self.screen_height - self.slot_height - 5, self.slot_width, self.slot_height)

            # Фон всегда коричневый
            pygame.draw.rect(screen, self.bar_color, slot_rect, border_radius=10)

            # Проверяем, есть ли предмет
            available = self.is_available(item, inventory, tools)
            text_color = (255, 255, 255) if available else (128, 128, 128)  # Белый или серый

            # Текст
            text = self.font.render(label, True, text_color)
            text_rect = text.get_rect(center=slot_rect.center)
            screen.blit(text, text_rect)

            # Зеленое выделение на выбранном
            if item == current_tool:
                pygame.draw.rect(screen, (0, 255, 0), slot_rect, 3, border_radius=10)
                self.current_index = i

    def update(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def is_available(self, item, inventory, tools):
        if item in tools:
            return tools[item]
        elif item in inventory:
            return inventory[item] > 0
        return False

    def select_slot(self, index, inventory, tools):
        if 0 <= index < len(self.slots):
            item = self.slots[index][0]
            if self.is_available(item, inventory, tools):
                return item
        return None