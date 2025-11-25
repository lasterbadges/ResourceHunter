import time

class DayNightCycle:
    def __init__(self, day_length=60):  # day_length in seconds
        self.day_length = day_length
        self.start_time = time.time() - day_length * 0.5  # Начать с полудня (день)
        self.current_time = 0

    def update(self):
        self.current_time = (time.time() - self.start_time) % self.day_length

    def get_time_of_day(self):
        # Returns a value between 0 and 1, where 0 is midnight, 0.5 is noon
        return self.current_time / self.day_length

    def is_day(self):
        time_of_day = self.get_time_of_day()
        return 0.25 <= time_of_day <= 0.75  # Day from 6 AM to 6 PM

    def is_night(self):
        return not self.is_day()

    def get_light_intensity(self):
        # Returns light intensity from 0 (dark) to 1 (bright)
        time_of_day = self.get_time_of_day()
        if time_of_day < 0.25:
            return time_of_day / 0.25  # Dawn
        elif time_of_day < 0.5:
            return 1.0  # Day
        elif time_of_day < 0.75:
            return 1.0 - (time_of_day - 0.5) / 0.25  # Dusk
        else:
            return 0.0  # Night

    def get_visibility_radius(self):
        # Returns visibility radius in screen pixels, smoothly changing with light intensity
        light_intensity = self.get_light_intensity()
        return int((50 + 350 * light_intensity) * 1.2)  # Slightly larger: from 60 at night to 480 at day

    def create_light_around_player(self, player_position):
        # Creates light around the player to illuminate space
        # Returns light parameters: position, radius, intensity
        # For now, just returns basic parameters; objects will be implemented later
        light_radius = 15  # Fixed radius for player light (can be adjusted)
        light_intensity = 1.0  # Full intensity
        return {
            'position': player_position,
            'radius': light_radius,
            'intensity': light_intensity
        }

# Example usage:
# cycle = DayNightCycle()
# while True:
#     cycle.update()
#     print(f"Time of day: {cycle.get_time_of_day():.2f}, Light: {cycle.get_light_intensity():.2f}")
#     time.sleep(1)