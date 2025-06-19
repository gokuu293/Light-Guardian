import pygame
import os
import random
from settings import *


class MainMenu:
    def __init__(self):
        # Загрузка шрифтов
        font_path = os.path.join('assets', 'fonts', 'Nosifer', 'Nosifer-Regular.ttf')
        if os.path.exists(font_path):
            self.font_title = pygame.font.Font(font_path, 64)
        else:
            self.font_title = pygame.font.SysFont('Arial', 64)
            
        elite_path = os.path.join('assets', 'fonts', 'Special_Elite', 'SpecialElite-Regular.ttf')
        if os.path.exists(elite_path):
            self.font_menu = pygame.font.Font(elite_path, 32)
        else:
            self.font_menu = pygame.font.SysFont('Arial', 32)
            
        self.selected = 0
        # Добавляем пункт "Controls" в меню
        self.options = ["Start Game", "Controls", "Settings", "Exit"]
        
        # Создаем пульсирующий эффект для выбранного пункта меню
        self.pulse_value = 0
        self.pulse_direction = 1
        
        # Создаем фоновую текстуру
        self.background = self._create_dark_background()
        
        # Флаг полноэкранного режима
        self.fullscreen = FULLSCREEN
        
    def _create_dark_background(self):
        # Создаем текстуру тёмного фона с небольшими вариациями
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 4):
            for x in range(0, SCREEN_WIDTH, 4):
                darkness = random.randint(0, 20)  # Небольшие вариации темноты
                color = (darkness, darkness, darkness)
                pygame.draw.rect(bg, color, (x, y, 4, 4))
                
        return bg
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "start_game"
                    elif self.selected == 1:
                        return "controls"  # Новое действие для экрана управления
                    elif self.selected == 3:
                        return "exit"
                elif event.key == pygame.K_f:  # Переключение полноэкранного режима
                    self._toggle_fullscreen()
        return None
    
    def update(self):
        # Обновление пульсации выбранного пункта меню
        self.pulse_value += 0.05 * self.pulse_direction
        if self.pulse_value > 1.0:
            self.pulse_value = 1.0
            self.pulse_direction = -1
        elif self.pulse_value < 0.3:
            self.pulse_value = 0.3
            self.pulse_direction = 1
    
    def draw(self, screen):
        # Отображаем текстурированный фон
        screen.blit(self.background, (0, 0))
        
        # Добавляем затенение по краям (виньетирование)
        self._draw_vignette(screen)
        
        # Отображаем заголовок с эффектом свечения
        title = self.font_title.render("LIGHT GUARDIAN", True, (255, 191, 0))
        
        # Создаем эффект свечения
        glow_surface = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 191, 0, 50), (0, 0, title.get_width() + 20, title.get_height() + 20), border_radius=30)
        screen.blit(glow_surface, (SCREEN_WIDTH//2 - (title.get_width() + 20)//2, 90))
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Отображаем пункты меню
        for i, option in enumerate(self.options):
            if i == self.selected:
                # Анимированное свечение для выбранного пункта
                intensity = int(200 * self.pulse_value) + 55
                color = (255, intensity, 0)
            else:
                color = (200, 200, 200)
                
            text = self.font_menu.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300 + i*60))
            
        # Добавляем подсказку внизу экрана с информацией о полноэкранном режиме
        elite_path = os.path.join('assets', 'fonts', 'Special_Elite', 'SpecialElite-Regular.ttf')
        if os.path.exists(elite_path):
            hint_font = pygame.font.Font(elite_path, 16)
        else:
            hint_font = pygame.font.SysFont('Arial', 16)
        
        hint = hint_font.render("Use UP/DOWN to navigate, ENTER to select, F for fullscreen", True, (180, 180, 180))
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 40))
            
    def _draw_vignette(self, screen):
        # Создаем эффект затемнения по краям экрана (виньетирование)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Параметры виньетирования
        rect_size = 900
        rect_x = SCREEN_WIDTH // 2 - rect_size // 2
        rect_y = SCREEN_HEIGHT // 2 - rect_size // 2
        
        # Заполняем поверхность полупрозрачным черным цветом
        vignette.fill((0, 0, 0, 180))
        
        # Создаем градиент от центра к краям
        for i in range(100):
            size = rect_size - i*2
            x = SCREEN_WIDTH // 2 - size // 2
            y = SCREEN_HEIGHT // 2 - size // 2
            
            # Вычисляем прозрачность для текущего круга (более прозрачный к центру)
            alpha = 180 - int(180 * (1 - i/100))
            
            # Рисуем круг с текущей прозрачностью
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, size, size), 2)
        
        # Накладываем виньетку на экран
        screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _toggle_fullscreen(self):
        # Реализация переключения полноэкранного режима
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Используем текущее разрешение экрана
            current_w = pygame.display.Info().current_w
            current_h = pygame.display.Info().current_h
            pygame.display.set_mode((current_w, current_h), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))