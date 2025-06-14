import pygame
import math
from settings import *


class Flashlight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.battery = 100
        self.on = True
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.ray_length = 20  # Длина луча для проверки препятствий

    def update(self, mouse_x, mouse_y, player_x, player_y):
        self.x = player_x
        self.y = player_y
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        self.angle = math.atan2(dy, dx)
        
        if self.on:
            self.battery = max(0, self.battery - LIGHT_DRAIN)

    def draw(self, screen, camera, level):
        if not self.on or self.battery <= 0:
            return
            
        self.light_surface.fill((0, 0, 0, 0))
        angle_rad = math.radians(LIGHT_ANGLE)
        distance = LIGHT_RADIUS * (self.battery / 100)
        
        # Преобразуем координаты с учетом камеры
        player_screen_x, player_screen_y = camera.apply_point(self.x, self.y)
        
        # Создаем лучи света с проверкой на препятствия
        num_rays = 30  # Количество лучей для проверки
        points = [(player_screen_x, player_screen_y)]  # Начальная точка - позиция игрока
        
        for i in range(num_rays):
            # Угол текущего луча
            ray_angle = self.angle - angle_rad/2 + (angle_rad * i / (num_rays - 1))
            
            # Находим точку пересечения с препятствием или максимальную дистанцию
            ray_end_x, ray_end_y = self.cast_ray(
                self.x, self.y, ray_angle, distance, level.walls
            )
            
            # Преобразуем координаты конца луча с учетом камеры
            screen_x, screen_y = camera.apply_point(ray_end_x, ray_end_y)
            points.append((screen_x, screen_y))
        
        # Добавляем начальную точку в конец для замыкания полигона
        points.append((player_screen_x, player_screen_y))
        
        # Рисуем полигон света
        if len(points) > 2:
            pygame.draw.polygon(self.light_surface, LIGHT_AMBER, points)
            screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def cast_ray(self, x, y, angle, max_distance, walls):
        """Бросает луч из позиции (x, y) под углом angle и возвращает точку пересечения с препятствием"""
        # Шаг для проверки коллизий
        step = 10
        current_distance = 0
        
        while current_distance < max_distance:
            # Увеличиваем расстояние
            current_distance += step
            
            # Вычисляем новую позицию
            check_x = x + math.cos(angle) * current_distance
            check_y = y + math.sin(angle) * current_distance
            
            # Проверяем столкновение с стенами
            check_rect = pygame.Rect(check_x - 2, check_y - 2, 4, 4)
            for wall in walls:
                if wall.colliderect(check_rect):
                    return check_x, check_y
        
        # Если препятствий нет, возвращаем максимальную дистанцию
        return x + math.cos(angle) * max_distance, y + math.sin(angle) * max_distance

    def get_current_radius(self):
        return LIGHT_RADIUS * (self.battery / 100)