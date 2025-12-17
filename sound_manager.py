import pygame
import random

# Инициализация микшера
pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.current_music = None
        self.load_sounds()

    def load_sounds(self):
        """Загрузка всех звуков и музыки"""
        try:
            # Загружаем звуки из папки sounds
            self.sounds['build'] = pygame.mixer.Sound("sounds/build.mp3")
            self.sounds['build'].set_volume(0.4)

            self.sounds['destroying'] = pygame.mixer.Sound("sounds/destroying.mp3")
            self.sounds['destroying'].set_volume(0.5)

            self.sounds['lightning'] = pygame.mixer.Sound("sounds/lightning.mp3")
            self.sounds['lightning'].set_volume(0.6)

            # Создаем список звуков ударов
            self.sounds['punch'] = [
                pygame.mixer.Sound("sounds/punch1.mp3"),
                pygame.mixer.Sound("sounds/punch3.mp3")
            ]
            for punch_sound in self.sounds['punch']:
                punch_sound.set_volume(0.4)

        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")
            self.sounds = {}

    def play_sound(self, sound_name):
        """Воспроизведение звука по имени"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def play_random_punch(self):
        """Воспроизведение случайного звука удара"""
        if 'punch' in self.sounds and self.sounds['punch']:
            try:
                random.choice(self.sounds['punch']).play()
            except:
                pass

    def play_night_music(self):
        """Воспроизведение ночной музыки"""
        if not self.music_playing or self.current_music != 'night':
            try:
                pygame.mixer.music.load("sounds/night.mp3")
                pygame.mixer.music.set_volume(0.3)  # Умеренная громкость
                pygame.mixer.music.play(-1)  # Зацикливание
                self.music_playing = True
                self.current_music = 'night'
                print("Ночная музыка включена")
            except Exception as e:
                print(f"Ошибка загрузки ночной музыки: {e}")

    def stop_music(self):
        """Остановка музыки"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.current_music = None
            print("Музыка остановлена")


# Глобальный экземпляр менеджера звуков
sound_manager = SoundManager()