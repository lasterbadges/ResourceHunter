import time


class DayNightCycle:
    def __init__(self, day_length=300):  # day_length in seconds
        self.day_length = day_length
        self.start_time = time.time() - day_length * 0.25  # Начать утром (6 AM)
        self.current_time = 0

    def update(self):
        self.current_time = (time.time() - self.start_time) % self.day_length

    def set_time(self, time_value):
        """Установить конкретное время (в секундах)"""
        self.start_time = time.time() - time_value

    def get_time_of_day(self):
        """Возвращает значение от 0 до 1, где 0 - полночь, 0.5 - полдень"""
        return self.current_time / self.day_length

    def is_day(self):
        time_of_day = self.get_time_of_day()
        return 0.25 <= time_of_day <= 0.75  # День с 6 утра до 6 вечера

    def is_night(self):
        return not self.is_day()

    def get_day_percentage(self):
        """Возвращает процент дня (0-100) для плавных переходов"""
        time_of_day = self.get_time_of_day()
        if time_of_day < 0.25:  # Ночь (0-6 утра)
            return 0
        elif time_of_day < 0.5:  # Утро (6-12)
            return ((time_of_day - 0.25) / 0.25) * 50
        elif time_of_day < 0.75:  # День (12-18)
            return 50 + ((time_of_day - 0.5) / 0.25) * 50
        else:  # Вечер/Ночь (18-24)
            return 100

    def get_light_intensity(self):
        """Возвращает интенсивность света от 0 (темно) до 1 (ярко)"""
        time_of_day = self.get_time_of_day()
        if time_of_day < 0.25:
            return time_of_day / 0.25  # Рассвет
        elif time_of_day < 0.5:
            return 1.0  # День
        elif time_of_day < 0.75:
            return 1.0 - (time_of_day - 0.5) / 0.25  # Закат
        else:
            return 0.0  # Ночь

    def get_visibility_radius(self):
        """Возвращает радиус видимости в пикселях, плавно меняющийся с интенсивностью света"""
        light_intensity = self.get_light_intensity()
        return int((150 + 350 * light_intensity) * 1.2)  # От 180 ночью до 480 днем

    def create_light_around_player(self, player_position):
        """Создает свет вокруг игрока для освещения пространства"""
        light_radius = 15  # Фиксированный радиус света игрока
        light_intensity = 1.0  # Полная интенсивность
        return {
            'position': player_position,
            'radius': light_radius,
            'intensity': light_intensity
        }

# Пример использования:
# cycle = DayNightCycle()
# while True:
#     cycle.update()
#     print(f"Time of day: {cycle.get_time_of_day():.2f}, Light: {cycle.get_light_intensity():.2f}")
#     time.sleep(1)