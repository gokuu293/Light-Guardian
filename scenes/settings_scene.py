import pygame
import os
import random
from settings import *

class SettingsScene:
    def __init__(self, sound_manager=None):
        # Звуковой менеджер
        self.sound_manager = sound_manager
        
        # Загрузка шрифтов
        font_path = os.path.join('assets', 'fonts', 'Nosifer', 'Nosifer-Regular.ttf')
        if os.path.exists(font_path):
            self.font_title = pygame.font.Font(font_path, 48)
        else:
            self.font_title = pygame.font.SysFont('Arial', 48)
            
        elite_path = os.path.join('assets', 'fonts', 'Special_Elite', 'SpecialElite-Regular.ttf')
        if os.path.exists(elite_path):
            self.font_text = pygame.font.Font(elite_path, 24)
            self.font_subtitle = pygame.font.Font(elite_path, 32)
        else:
            self.font_text = pygame.font.SysFont('Arial', 24)
            self.font_subtitle = pygame.font.SysFont('Arial', 32)
        
        # Фон
        self.background = self._create_dark_background()
        
        # Настройки громкости
        self.settings_options = [
            {"name": "Sound Effects Volume", "value": SOUND_VOLUME * 100, "min": 0, "max": 100},
            {"name": "Music Volume", "value": MUSIC_VOLUME * 100, "min": 0, "max": 100}
        ]
        
        self.selected_option = 0
        
        # Для плавной анимации
        self.pulse_value = 0.5
        self.pulse_direction = 1

    def _create_dark_background(self):
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 4):
            for x in range(0, SCREEN_WIDTH, 4):
                darkness = random.randint(0, 20)
                color = (darkness, darkness, darkness)
                pygame.draw.rect(bg, color, (x, y, 4, 4))
        return bg
        
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self._apply_settings()
                    if self.sound_manager:
                        self.sound_manager.play_sound("menu_select")
                    return "back_from_settings" 
                
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.settings_options)
                    if self.sound_manager:
                        self.sound_manager.play_sound("menu_change")
                
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.settings_options)
                    if self.sound_manager:
                        self.sound_manager.play_sound("menu_change")
                
                elif event.key == pygame.K_LEFT:
                    option = self.settings_options[self.selected_option]
                    option["value"] = max(option["min"], option["value"] - 10)
                    self._update_volume()
                    if self.sound_manager:
                        self.sound_manager.play_sound("menu_change")
                
                elif event.key == pygame.K_RIGHT:
                    option = self.settings_options[self.selected_option]
                    option["value"] = min(option["max"], option["value"] + 10)
                    self._update_volume()
                    if self.sound_manager:
                        self.sound_manager.play_sound("menu_change")
        
        return None
    
    def _update_volume(self):
        """Обновляет громкость в реальном времени"""
        if self.sound_manager:
            sound_vol = self.settings_options[0]["value"] / 100
            music_vol = self.settings_options[1]["value"] / 100
            self.sound_manager.set_sound_volume(sound_vol)
            self.sound_manager.set_music_volume(music_vol)
            
    def _apply_settings(self):
        """Применяет настройки при выходе"""
        global SOUND_VOLUME, MUSIC_VOLUME
        
        SOUND_VOLUME = self.settings_options[0]["value"] / 100
        MUSIC_VOLUME = self.settings_options[1]["value"] / 100
        
    def update(self):
        # Обновление пульсации выбранного элемента
        self.pulse_value += 0.05 * self.pulse_direction
        if self.pulse_value > 1.0:
            self.pulse_value = 1.0
            self.pulse_direction = -1
        elif self.pulse_value < 0.3:
            self.pulse_value = 0.3
            self.pulse_direction = 1
        
    def draw(self, screen):
        # Отображаем фон
        screen.blit(self.background, (0, 0))
        
        # Добавляем виньетку
        self._draw_vignette(screen)
        
        # Заголовок
        title = self.font_title.render("SETTINGS", True, (255, 191, 0))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Отображаем настройки
        y_pos = 150
        for i, option in enumerate(self.settings_options):
            # Определяем цвет и стиль в зависимости от выбора
            if i == self.selected_option:
                intensity = int(200 * self.pulse_value) + 55
                name_color = (255, intensity, 0)
                value_color = (255, intensity, 0)
            else:
                name_color = (200, 200, 200)
                value_color = (180, 180, 180)
            
            # Отображаем название настройки
            name_text = self.font_subtitle.render(option["name"], True, name_color)
            screen.blit(name_text, (SCREEN_WIDTH//4, y_pos))
            
            # Отображаем ползунок громкости
            slider_width = 300
            slider_height = 10
            slider_x = SCREEN_WIDTH//2
            slider_y = y_pos + name_text.get_height() + 15
            
            # Рамка ползунка
            pygame.draw.rect(screen, (100, 100, 100), 
                             (slider_x, slider_y, slider_width, slider_height))
            
            # Заполнение ползунка
            fill_width = int((option["value"] / option["max"]) * slider_width)
            pygame.draw.rect(screen, value_color, 
                             (slider_x, slider_y, fill_width, slider_height))
            
            # Отображаем текущее значение
            value_text = self.font_text.render(f"{int(option['value'])}%", True, value_color)
            screen.blit(value_text, 
                       (slider_x + slider_width + 20, slider_y - value_text.get_height()//2 + slider_height//2))
            
            y_pos += 100
        
        # Инструкция для управления
        help_text = self.font_text.render("Use LEFT/RIGHT to adjust, UP/DOWN to navigate", True, (150, 150, 150))
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 80))
        
        # Инструкция для возврата
        back_text = self.font_text.render("Press ESC to save and return", True, (150, 150, 150))
        screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, SCREEN_HEIGHT - 40))
    
    def _draw_vignette(self, screen):
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        rect_size = 900
        
        vignette.fill((0, 0, 0, 180))
        
        for i in range(100):
            size = rect_size - i*2
            x = SCREEN_WIDTH // 2 - size // 2
            y = SCREEN_HEIGHT // 2 - size // 2
            
            alpha = 180 - int(180 * (1 - i/100))
            
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, size, size), 2)
        
        screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT) 