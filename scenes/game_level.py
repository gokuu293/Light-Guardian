import pygame
import os
import math
from settings import *
from entities.player import Player
from entities.camera import Camera
from levels.level1 import Level1


class GameLevel:
    def __init__(self):
        self.level = Level1()
        # Создаем игрока в стартовой позиции уровня
        start_x, start_y = self.level.start_position
        self.player = Player(start_x, start_y)
        self.camera = Camera()
        self.camera.set_target(self.player)
        
        # Загружаем шрифты
        elite_path = os.path.join('assets', 'fonts', 'Special_Elite', 'SpecialElite-Regular.ttf')
        if os.path.exists(elite_path):
            self.font = pygame.font.Font(elite_path, 24)
        else:
            self.font = pygame.font.SysFont('Arial', 24)
            
        self.game_state = "playing"  # playing, game_over, level_complete, paused
        self.message_timer = 0
        self.fullscreen = FULLSCREEN
        
        # Поверхность для создания маски темноты
        self.darkness_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Эффект темноты включен
        self.darkness_enabled = True
        
        # Сбрасываем флаг начального спавна врагов
        self.level.enemy_manager.initial_spawn_done = False
        
        # Опции в меню паузы
        self.pause_options = ["Resume", "Controls", "Quit to Menu"]
        self.selected_pause_option = 0
        self.pulse_value = 0.5
        self.pulse_direction = 1

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                        return None
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                        return None
                    elif self.game_state == "game_over":
                        return "menu"
                elif event.key == pygame.K_r and self.game_state == "game_over":
                    self.__init__()  # Перезапуск уровня
                elif event.key == pygame.K_SPACE and self.game_state == "level_complete":
                    return "menu"  # Возвращаемся в меню
                elif event.key == pygame.K_f:  # Переключение полноэкранного режима
                    self._toggle_fullscreen()
                elif event.key == pygame.K_l:  # Переключение эффекта темноты (для отладки)
                    self.darkness_enabled = not self.darkness_enabled
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:  # Приблизить камеру
                    self.camera.adjust_zoom(0.1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:  # Отдалить камеру
                    self.camera.adjust_zoom(-0.1)
                    
                # Обработка управления в меню паузы
                if self.game_state == "paused":
                    if event.key == pygame.K_DOWN:
                        self.selected_pause_option = (self.selected_pause_option + 1) % len(self.pause_options)
                    elif event.key == pygame.K_UP:
                        self.selected_pause_option = (self.selected_pause_option - 1) % len(self.pause_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_pause_option == 0:  # Resume
                            self.game_state = "playing"
                        elif self.selected_pause_option == 1:  # Controls
                            return "controls"
                        elif self.selected_pause_option == 2:  # Quit to Menu
                            return "menu"
        
        if self.game_state == "playing":
            self.player.handle_input(events, self.level, self.camera)
        return None

    def update(self):
        if self.game_state == "playing":
            # Обновление камеры с учетом размеров карты
            self.camera.update(self.level.width, self.level.height)
            level_result = self.level.update(self.player)
            
            if level_result == "game_over":
                self.game_state = "game_over"
                self.message_timer = 180  # 3 секунды
            elif level_result == "level_complete":
                self.game_state = "level_complete"
                self.message_timer = 180
        elif self.game_state == "paused":
            # Обновление пульсации выбранного пункта меню
            self.pulse_value += 0.05 * self.pulse_direction
            if self.pulse_value > 1.0:
                self.pulse_value = 1.0
                self.pulse_direction = -1
            elif self.pulse_value < 0.3:
                self.pulse_value = 0.3
                self.pulse_direction = 1
        else:
            if self.message_timer > 0:
                self.message_timer -= 1

    def draw(self, screen):
        screen.fill(BLACK)
        
        # Отрисовка уровня и игрока с учетом камеры
        self.level.draw(screen, self.camera)
        self.player.draw(screen, self.camera, self.level)

        # Если эффект темноты включен, применяем его
        if self.darkness_enabled:
            self._apply_darkness_effect(screen)
        
        # Обновленный HUD для отображения заряда батареи
        self._draw_battery_indicator(screen)
        
        # Отрисовка сообщений о состоянии игры
        if self.game_state == "game_over":
            self.draw_message(screen, "GAME OVER", "Press R to restart or ESC to quit")
        elif self.game_state == "level_complete":
            self.draw_message(screen, "LEVEL COMPLETE!", "Press SPACE to continue")
        elif self.game_state == "paused":
            self._draw_pause_menu(screen)
    
    def _apply_darkness_effect(self, screen):
        """Применяет эффект темноты, оставляя видимыми только области вокруг игрока и фонарика"""
        self.darkness_surface.fill((0, 0, 0, 180))
        
        # Получаем позицию игрока на экране
        player_screen_pos = self.camera.apply(self.player.rect)
        player_screen_x, player_screen_y = player_screen_pos.centerx, player_screen_pos.centery
        
        # Создаем увеличенную видимую область вокруг игрока (базовое освещение)
        # Учитываем масштаб камеры для корректного размера света
        base_light_radius = 110 * self.camera.zoom
        pygame.draw.circle(self.darkness_surface, (0, 0, 0, 0), 
                          (player_screen_x, player_screen_y), base_light_radius)
        
        # Если фонарик включен, добавляем его свет
        if self.player.flashlight.on and self.player.flashlight.battery > 0:
            angle_rad = math.radians(LIGHT_ANGLE)
            # Учитываем масштаб камеры для радиуса света фонарика
            distance = LIGHT_RADIUS * (self.player.flashlight.battery / 100) * self.camera.zoom
            
            # Создаем конус света
            flash_points = [(player_screen_x, player_screen_y)]
            num_rays = 15
            
            # Угол фонарика (направление мыши)
            light_angle = self.player.flashlight.angle
            
            # Собираем точки для полигона конуса света
            for i in range(num_rays + 1):
                ray_angle = light_angle - angle_rad/2 + (angle_rad * i / num_rays)
                end_x = player_screen_x + math.cos(ray_angle) * distance
                end_y = player_screen_y + math.sin(ray_angle) * distance
                flash_points.append((end_x, end_y))
            
            # Рисуем полигон света с нулевой прозрачностью
            if len(flash_points) > 2:
                pygame.draw.polygon(self.darkness_surface, (0, 0, 0, 0), flash_points)
        
        # Накладываем темную маску на игровой экран
        screen.blit(self.darkness_surface, (0, 0))
            
    def draw_message(self, screen, title, subtitle):
        # Затемнение экрана
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Загружаем шрифты для заголовка
        nosifer_path = os.path.join('assets', 'fonts', 'Nosifer', 'Nosifer-Regular.ttf')
        if os.path.exists(nosifer_path):
            title_font = pygame.font.Font(nosifer_path, 64)
        else:
            title_font = pygame.font.SysFont('Arial', 64)
        
        # Отрисовка заголовка
        title_text = title_font.render(title, True, (255, 191, 0))
        
        # Создаем эффект свечения вокруг текста
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 191, 0, 50), (0, 0, title_text.get_width() + 20, title_text.get_height() + 20), border_radius=30)
        screen.blit(glow_surface, (SCREEN_WIDTH//2 - (title_text.get_width() + 20)//2, SCREEN_HEIGHT//2 - 60))
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Отрисовка подзаголовка
        subtitle_text = self.font.render(subtitle, True, WHITE)
        screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def _toggle_fullscreen(self):
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN
        if FULLSCREEN:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def _draw_battery_indicator(self, screen):
        # Размеры и положение индикатора
        bar_width = 150
        bar_height = 20
        x_pos = 20
        y_pos = 20
        border = 2
        
        # Рисуем контур батарейки
        pygame.draw.rect(screen, WHITE, (x_pos, y_pos, bar_width, bar_height), border)
        
        # Рисуем маленький выступ справа батарейки
        pygame.draw.rect(screen, WHITE, (x_pos + bar_width, y_pos + 5, 5, bar_height - 10))
        
        # Заполняем индикатор в зависимости от заряда
        charge_width = int((bar_width - 2 * border) * (self.player.flashlight.battery / 100))
        
        # Определяем цвет на основе уровня заряда
        if self.player.flashlight.battery > 70:
            charge_color = (0, 255, 0)  # Зеленый для высокого заряда
        elif self.player.flashlight.battery > 30:
            charge_color = (255, 255, 0)  # Желтый для среднего заряда
        else:
            # Красный мигающий для низкого заряда
            if pygame.time.get_ticks() % 1000 < 500 and self.player.flashlight.battery < 15:
                charge_color = (255, 0, 0)
            else:
                charge_color = (200, 0, 0)
        
        # Рисуем заполнение
        if charge_width > 0:
            pygame.draw.rect(screen, charge_color, 
                            (x_pos + border, y_pos + border, 
                             charge_width, bar_height - 2 * border))
        
        # Отображаем текст с процентом заряда
        battery_text = self.font.render(f"{int(self.player.flashlight.battery)}%", 
                                       True, WHITE)
        screen.blit(battery_text, (x_pos + bar_width + 15, y_pos - 2))
        
        # Значок фонарика
        flashlight_icon_x = x_pos - 30
        pygame.draw.polygon(screen, WHITE if self.player.flashlight.on else (100, 100, 100), 
                            [(flashlight_icon_x, y_pos + 10), 
                             (flashlight_icon_x - 8, y_pos), 
                             (flashlight_icon_x - 8, y_pos + 20)])
        pygame.draw.rect(screen, WHITE if self.player.flashlight.on else (100, 100, 100), 
                        (flashlight_icon_x, y_pos + 3, 15, 14))

    def _draw_pause_menu(self, screen):
        # Затемнение экрана
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Загружаем шрифты для заголовка
        nosifer_path = os.path.join('assets', 'fonts', 'Nosifer', 'Nosifer-Regular.ttf')
        if os.path.exists(nosifer_path):
            title_font = pygame.font.Font(nosifer_path, 54)
        else:
            title_font = pygame.font.SysFont('Arial', 54)
        
        # Отрисовка заголовка
        title_text = title_font.render("PAUSED", True, (255, 191, 0))
        
        # Создаем эффект свечения вокруг текста
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 191, 0, 50), (0, 0, title_text.get_width() + 20, title_text.get_height() + 20), border_radius=30)
        screen.blit(glow_surface, (SCREEN_WIDTH//2 - (title_text.get_width() + 20)//2, SCREEN_HEIGHT//2 - 160))
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 150))
        
        # Отображаем пункты меню
        elite_path = os.path.join('assets', 'fonts', 'Special_Elite', 'SpecialElite-Regular.ttf')
        if os.path.exists(elite_path):
            menu_font = pygame.font.Font(elite_path, 32)
        else:
            menu_font = pygame.font.SysFont('Arial', 32)
            
        for i, option in enumerate(self.pause_options):
            if i == self.selected_pause_option:
                # Анимированное свечение для выбранного пункта
                intensity = int(200 * self.pulse_value) + 55
                color = (255, intensity, 0)
            else:
                color = (200, 200, 200)
                
            text = menu_font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50 + i*60))
        
        # Добавляем подсказку внизу экрана
        hint_font = pygame.font.SysFont('Arial', 18)
        hint = hint_font.render("Use UP/DOWN to navigate, ENTER to select, ESC to resume", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 40))