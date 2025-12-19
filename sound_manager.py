import pygame
import random
import os
import math
import sys

base_path = getattr(sys, '_MEIPASS', os.getcwd())

# Инициализация микшера
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.current_music = None
        self.target_volume = 0.15
        self.current_volume = 0
        self.fade_speed = 0.003
        self.music_fading_in = False
        self.music_fading_out = False
        self.day_music_volume = 0.15
        self.night_music_volume = 0.25
        self.game_over_active = False
        self.player_x = 0  # Для 3D эффекта
        self.player_y = 0
        self.load_sounds()
        print(f"Звуковой менеджер инициализирован. Загружено звуков: {len(self.sounds)}")

    def update_player_position(self, x, y):
        """Обновить позицию игрока для 3D эффекта"""
        self.player_x = x
        self.player_y = y

    def load_sounds(self):
        """Загрузка всех звуков и музыки"""
        sound_files = {
            'build': "sounds/build.mp3",
            'destroying': "sounds/destroying.mp3",
            'lightning': "sounds/lightning.mp3",
            'punch': ["sounds/punch1.mp3", "sounds/punch3.mp3"],
            # NPC звуки
            'mops': ["sounds/mops.mp3"],
            'sheep': ["sounds/sheep1.mp3", "sounds/sheep2.mp3"],
            'boss': ["sounds/boss1.mp3", "sounds/boss2.mp3", "sounds/boss3.mp3"],
            'wolf': ["sounds/wolf1.mp3", "sounds/wolf2.mp3", "sounds/wolf3.mp3"]
        }

        # Загружаем все звуки
        for sound_name, filepaths in sound_files.items():
            if isinstance(filepaths, list):
                # Для звуков со списком вариантов
                self.sounds[sound_name] = []
                for i, filepath in enumerate(filepaths):
                    full_filepath = os.path.join(base_path, filepath)
                    try:
                        if os.path.exists(full_filepath):
                            sound = pygame.mixer.Sound(full_filepath)
                            # Устанавливаем базовую громкость
                            if sound_name == 'mops':
                                sound.set_volume(0.4)
                            elif sound_name == 'sheep':
                                sound.set_volume(0.3)
                            elif sound_name == 'boss':
                                sound.set_volume(0.6)
                            elif sound_name == 'wolf':
                                sound.set_volume(0.5)
                            elif sound_name == 'punch':
                                sound.set_volume(0.4)
                            elif sound_name == 'build':
                                sound.set_volume(0.4)
                            elif sound_name == 'destroying':
                                sound.set_volume(0.5)
                            elif sound_name == 'lightning':
                                sound.set_volume(0.6)

                            self.sounds[sound_name].append(sound)
                            print(f"✓ Звук {sound_name}{i + 1} загружен")
                        else:
                            print(f"✗ Файл не найден: {full_filepath}")
                            self.sounds[sound_name].append(None)
                    except Exception as e:
                        print(f"Ошибка загрузки {full_filepath}: {e}")
                        self.sounds[sound_name].append(None)
            else:
                # Для одиночных звуков
                full_filepath = os.path.join(base_path, filepaths)
                try:
                    if os.path.exists(full_filepath):
                        sound = pygame.mixer.Sound(full_filepath)
                        sound.set_volume(0.5)
                        self.sounds[sound_name] = sound
                        print(f"✓ Звук {sound_name} загружен")
                    else:
                        print(f"✗ Файл не найден: {full_filepath}")
                        self.sounds[sound_name] = None
                except Exception as e:
                    print(f"Ошибка загрузки {full_filepath}: {e}")
                    self.sounds[sound_name] = None

    def update(self):
        """Обновление плавного изменения громкости"""
        if self.game_over_active:
            return

        if self.current_volume < 0:
            self.current_volume = 0

        if abs(self.current_volume - self.target_volume) > 0.001:
            diff = self.target_volume - self.current_volume
            if abs(diff) < self.fade_speed:
                self.current_volume = self.target_volume
            else:
                self.current_volume += self.fade_speed if diff > 0 else -self.fade_speed

            self.current_volume = max(0, min(self.current_volume, self.night_music_volume))

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(self.current_volume)

        if self.music_fading_out and self.current_volume <= 0.01:
            pygame.mixer.music.stop()
            self.current_music = None
            self.music_fading_out = False
            self.current_volume = 0
            self.target_volume = 0

    def calculate_distance_volume(self, npc_x, npc_y, max_distance=500):
        """Рассчитать громкость звука в зависимости от расстояния до игрока"""
        if not hasattr(self, 'player_x') or not hasattr(self, 'player_y'):
            return 1.0  # Если позиция игрока неизвестна, полная громкость

        dx = npc_x - self.player_x
        dy = npc_y - self.player_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance >= max_distance:
            return 0.1  # Минимальная громкость на максимальном расстоянии
        elif distance <= 50:
            return 1.0  # Полная громкость вблизи
        else:
            # Плавное уменьшение громкости с расстоянием
            volume = 1.0 - (distance / max_distance) * 0.9
            return max(0.1, min(1.0, volume))

    def play_npc_sound(self, npc_type, npc_x=None, npc_y=None):
        """Воспроизвести случайный звук NPC с 3D эффектом"""
        if npc_type not in self.sounds or not self.sounds[npc_type]:
            return

        # Выбираем случайный звук из доступных
        available_sounds = [s for s in self.sounds[npc_type] if s is not None]
        if not available_sounds:
            return

        sound = random.choice(available_sounds)

        # Рассчитываем громкость на основе расстояния
        if npc_x is not None and npc_y is not None:
            volume = self.calculate_distance_volume(npc_x, npc_y)
            sound.set_volume(volume)

        try:
            sound.play()
            # print(f"Воспроизведен звук {npc_type} (громкость: {volume:.2f})")
        except:
            pass

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

    def set_game_over(self, active):
        self.game_over_active = active
        if active:
            pygame.mixer.music.stop()
            self.current_music = None
            self.current_volume = 0
            self.target_volume = 0
            print("Музыка остановлена (game over)")

    def play_day_music(self):
        if self.game_over_active:
            return

        if self.current_music != 'day':
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

                music_path = os.path.join(base_path, "sounds/day.mp3")
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.play(-1)

                self.current_music = 'day'
                self.target_volume = self.day_music_volume
                self.current_volume = 0
                self.music_fading_in = True
                self.music_fading_out = False
                print("Дневная музыка включена (тихая)")

            except Exception as e:
                print(f"Ошибка загрузки дневной музыки: {e}")

    def play_night_music(self):
        if self.game_over_active:
            return

        if self.current_music != 'night':
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

                music_path = os.path.join(base_path, "sounds/night.mp3")
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.play(-1)

                self.current_music = 'night'
                self.target_volume = self.night_music_volume
                self.current_volume = 0
                self.music_fading_in = True
                self.music_fading_out = False
                print("Ночная музыка включена")

            except Exception as e:
                print(f"Ошибка загрузки ночной музыки: {e}")

    def stop_music(self):
        if self.current_music and pygame.mixer.music.get_busy():
            self.target_volume = 0
            self.music_fading_out = True
            print(f"Музыка '{self.current_music}' плавно выключается")

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def unpause_music(self):
        if not self.game_over_active:
            pygame.mixer.music.unpause()

    def reset_for_new_game(self):
        self.game_over_active = False
        self.current_music = None
        self.current_volume = 0
        self.target_volume = 0
        print("Музыка сброшена для новой игры")


sound_manager = SoundManager()