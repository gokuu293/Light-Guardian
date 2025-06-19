import pygame
from settings import *

class Camera:
    def __init__(self):
        # Прямоугольник камеры, определяющий видимую область
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.target = None
        
        # Добавляем параметр масштаба (zoom)
        self.zoom = 1.5  # Значение больше 1 - приближение, меньше 1 - отдаление
        
        # Фактические размеры области просмотра с учетом масштаба
        self.view_width = int(self.width / self.zoom)
        self.view_height = int(self.height / self.zoom)
        
    def set_target(self, target):
        """Установить цель для слежения камерой"""
        self.target = target
    
    def update(self, map_width, map_height):
        """Обновить положение камеры, следуя за целью"""
        if not self.target:
            return
            
        # Обновляем фактические размеры видимой области с учетом масштаба
        self.view_width = int(self.width / self.zoom)
        self.view_height = int(self.height / self.zoom)
            
        # Центрирование камеры на игроке
        self.rect.x = self.target.rect.centerx - self.view_width // 2
        self.rect.y = self.target.rect.centery - self.view_height // 2
        
        # Ограничение камеры границами карты
        self.rect.x = max(0, min(self.rect.x, map_width - self.view_width))
        self.rect.y = max(0, min(self.rect.y, map_height - self.view_height))
    
    def apply(self, entity_rect):
        """Применить смещение камеры к координатам объекта с учетом масштаба"""
        # Преобразуем координаты объекта относительно камеры
        screen_x = (entity_rect.x - self.rect.x) * self.zoom
        screen_y = (entity_rect.y - self.rect.y) * self.zoom
        
        # Преобразуем размеры объекта с учетом масштаба
        screen_width = entity_rect.width * self.zoom
        screen_height = entity_rect.height * self.zoom
        
        return pygame.Rect(screen_x, screen_y, screen_width, screen_height)
    
    def apply_point(self, x, y):
        """Применить смещение камеры к точке с учетом масштаба"""
        screen_x = (x - self.rect.x) * self.zoom
        screen_y = (y - self.rect.y) * self.zoom
        return (screen_x, screen_y)
    
    def apply_rect(self, rect):
        """Применить смещение камеры к прямоугольнику с учетом масштаба"""
        screen_x = (rect.x - self.rect.x) * self.zoom
        screen_y = (rect.y - self.rect.y) * self.zoom
        screen_width = rect.width * self.zoom
        screen_height = rect.height * self.zoom
        
        return pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        
    def adjust_zoom(self, amount):
        """Изменить масштаб камеры"""
        # Ограничиваем масштаб от 0.5 (отдалено) до 2.5 (сильно приближено)
        self.zoom = max(0.5, min(2.5, self.zoom + amount))