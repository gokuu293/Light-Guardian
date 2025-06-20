import pygame
import os
from settings import *

class SoundManager:
    def __init__(self):
        # Инициализируем микшер pygame
        pygame.mixer.init()
        
        # Словари для хранения звуков
        self.sounds = {}
        
        # Загружаем звуки
        self.load_sounds()
        
    def load_sounds(self):
        """Загружает все звуковые файлы из папки assets/sounds"""
        sound_files = {
            "enemy_detect": "enemy_detect.mp3",
            "footstep": "footstep.mp3",
            "battery_pickup": "battery_pickup.mp3",
            "player_damage": "player_damage.mp3",
            "menu_select": "menu_select.mp3",
            "menu_change": "menu_change.mp3",
            "menu_background": "menu_background.mp3",
            "level_complete": "level_complete.mp3",
            "light_hit_enemy": "light_hit_enemy.mp3"
        }
        
        for name, filename in sound_files.items():
            self.load_sound(name, filename)
            
    def load_sound(self, name, filename):
        """Загружает отдельный звуковой файл"""
        try:
            sound_path = os.path.join("assets", "sounds", filename)
            self.sounds[name] = pygame.mixer.Sound(sound_path)
            # Установка громкости с учетом типа звука
            if "menu_background" in name:
                self.sounds[name].set_volume(MUSIC_VOLUME)
            else:
                self.sounds[name].set_volume(SOUND_VOLUME)
        except pygame.error as e:
            print(f"Не удалось загрузить звук: {filename}. Ошибка: {e}")
            
    def play_sound(self, name, loops=0):
        """Воспроизводит звук по его имени"""
        if name in self.sounds and SOUND_ENABLED:
            # Для шагов используем упрощенную логику
            if name == "footstep":
                # Если звук уже воспроизводится, не запускаем новый
                for channel_id in range(pygame.mixer.get_num_channels()):
                    channel = pygame.mixer.Channel(channel_id)
                    if channel.get_busy() and channel.get_sound() == self.sounds[name]:
                        return
                # Воспроизводим звук шагов
                self.sounds[name].play(loops)
            else:
                self.sounds[name].play(loops)
            
    def play_menu_music(self):
        """Запускает фоновую музыку меню"""
        if MUSIC_ENABLED and "menu_background" in self.sounds:
            # Останавливаем текущую музыку если играет
            pygame.mixer.music.stop()
            
            # Воспроизводим музыку меню (в бесконечном цикле)
            self.sounds["menu_background"].play(-1)
                
    def stop_music(self):
        """Останавливает всю музыку"""
        pygame.mixer.music.stop()
        if "menu_background" in self.sounds:
            self.sounds["menu_background"].stop()

    def set_sound_volume(self, volume):
        """Устанавливает громкость звуковых эффектов"""
        volume = max(0.0, min(1.0, volume))  # Ограничиваем значение от 0 до 1
        
        # Обновляем громкость для всех звуков кроме музыки меню
        for name, sound in self.sounds.items():
            if name != "menu_background":
                sound.set_volume(volume)
        
        # Обновляем глобальную настройку громкости
        global SOUND_VOLUME
        SOUND_VOLUME = volume

    def set_music_volume(self, volume):
        """Устанавливает громкость музыки"""
        volume = max(0.0, min(1.0, volume))  # Ограничиваем значение от 0 до 1
        
        # Обновляем громкость фоновой музыки
        if "menu_background" in self.sounds:
            self.sounds["menu_background"].set_volume(volume)
        
        # Обновляем глобальную настройку громкости
        global MUSIC_VOLUME
        MUSIC_VOLUME = volume