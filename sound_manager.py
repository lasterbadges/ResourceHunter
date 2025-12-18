import pygame
import random

# Инициализация микшера
pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.current_music = None
        self.music_volume = 0.3  # Стандартная громкость
        self.fade_speed = 0.01  # Скорость плавного перехода
        self.target_volume = 0.3  # Целевая громкость
        self.fading_out = False
        self.fading_in = False
        self.next_music = None
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

    def update(self):
        """Обновление плавного перехода музыки"""
        if self.fading_out:
            # Плавное уменьшение громкости
            self.music_volume = max(0, self.music_volume - self.fade_speed)
            pygame.mixer.music.set_volume(self.music_volume)

            if self.music_volume <= 0:
                self.fading_out = False
                if self.next_music:
                    self._switch_music(self.next_music)
                    self.next_music = None
                    self.fading_in = True
                else:
                    pygame.mixer.music.stop()
                    self.music_playing = False
                    self.current_music = None

        elif self.fading_in:
            # Плавное увеличение громкости
            self.music_volume = min(self.target_volume, self.music_volume + self.fade_speed)
            pygame.mixer.music.set_volume(self.music_volume)

            if self.music_volume >= self.target_volume:
                self.fading_in = False

    def _switch_music(self, music_type):
        """Внутренний метод для переключения музыки"""
        try:
            if music_type == 'day':
                pygame.mixer.music.load("sounds/day.mp3")
            elif music_type == 'night':
                pygame.mixer.music.load("sounds/night.mp3")

            pygame.mixer.music.set_volume(0)  # Начинаем с нулевой громкости
            pygame.mixer.music.play(-1)  # Зацикливание
            self.music_playing = True
            self.current_music = music_type
            print(f"Музыка переключена на: {music_type}")
        except Exception as e:
            print(f"Ошибка переключения музыки на {music_type}: {e}")
            self.music_playing = False
            self.current_music = None

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

    def play_day_music(self):
        """Воспроизведение дневной музыки с плавным переходом"""
        if self.current_music != 'day':
            if self.music_playing:
                # Если играет другая музыка, начинаем плавный переход
                self.fading_out = True
                self.next_music = 'day'
            else:
                # Если музыка не играет, просто включаем
                self._switch_music('day')
                self.music_volume = 0
                self.fading_in = True

    def play_night_music(self):
        """Воспроизведение ночной музыки с плавным переходом"""
        if self.current_music != 'night':
            if self.music_playing:
                # Если играет другая музыка, начинаем плавный переход
                self.fading_out = True
                self.next_music = 'night'
            else:
                # Если музыка не играет, просто включаем
                self._switch_music('night')
                self.music_volume = 0
                self.fading_in = True

    def stop_music_fade(self):
        """Плавная остановка музыки"""
        if self.music_playing:
            self.fading_out = True
            self.next_music = None

    def stop_music(self):
        """Немедленная остановка музыки"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.current_music = None
            self.fading_out = False
            self.fading_in = False
            self.next_music = None
            print("Музыка остановлена")


# Глобальный экземпляр менеджера звуков
sound_manager = SoundManager()