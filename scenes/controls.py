import pygame
import os
import random
from settings import *

class ControlsScene:
    def __init__(self):
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
                    return "back_from_controls"  # Специальный флаг для возврата
        return None
        
    def update(self):
        pass
        
    def draw(self, screen):
        # Отображаем фон
        screen.blit(self.background, (0, 0))
        
        # Добавляем виньетку
        self._draw_vignette(screen)
        
        # Заголовок
        title = self.font_title.render("CONTROLS", True, (255, 191, 0))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Информация об управлении
        controls = [
            {"title": "Movement", "keys": [
                "W - Move up",
                "A - Move left",
                "S - Move down",
                "D - Move right",
                "Mouse - Aim flashlight"
            ]},
            {"title": "Flashlight", "keys": [
                "Mouse - Aim flashlight",
                "Collect batteries to recharge"
            ]},
            {"title": "Game Controls", "keys": [
                "ESC - Return to menu",
                "F - Toggle fullscreen",
                "+ / - : Adjust camera zoom",
                "L - Toggle darkness effect (debug)",
                "R - Restart (when game over)"
            ]}
        ]
        
        # Рассчитываем общую высоту всех элементов, чтобы не допустить наложения на инструкцию возврата
        total_height = 0
        for section in controls:
            total_height += 50  # Высота заголовка раздела
            total_height += len(section["keys"]) * 30  # Высота каждого пункта управления
            total_height += 20  # Дополнительное пространство после раздела
        
        # Начинаем отрисовку с верхней точки, чтобы уместить все элементы
        y_start = 150
        if total_height > SCREEN_HEIGHT - 150 - 70:  # Проверяем, умещается ли всё на экране
            y_start = 120  # Если нет, начинаем выше
        
        y_pos = y_start
        for section in controls:
            # Отображаем заголовок раздела
            subtitle = self.font_subtitle.render(section["title"], True, (200, 200, 200))
            screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, y_pos))
            y_pos += 50
            
            # Отображаем управление в этом разделе
            for key_info in section["keys"]:
                text = self.font_text.render(key_info, True, (180, 180, 180))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 30
            
            y_pos += 20
        
        # Инструкция для возврата - размещаем её с гарантированным отступом от последнего элемента
        back_text = self.font_text.render("Press ESC to return", True, (150, 150, 150))
        screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, SCREEN_HEIGHT - 30))
    
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