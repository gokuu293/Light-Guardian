import pygame
from settings import *

class Camera:
    def __init__(self):
        # Прямоугольник камеры, определяющий видимую область
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.target = None
        
    def set_target(self, target):
        """Установить цель для слежения камерой"""
        self.target = target
    
    def update(self, map_width, map_height):
        """Обновить положение камеры, следуя за целью"""
        if not self.target:
            return
            
        # Центрирование камеры на игроке
        self.rect.centerx = self.target.rect.centerx
        self.rect.centery = self.target.rect.centery
        
        # Ограничение камеры границами карты
        self.rect.x = max(0, min(self.rect.x, map_width - self.width))
        self.rect.y = max(0, min(self.rect.y, map_height - self.height))
    
    def apply(self, entity_rect):
        """Применить смещение камеры к координатам объекта"""
        return pygame.Rect(
            entity_rect.x - self.rect.x,
            entity_rect.y - self.rect.y,
            entity_rect.width,
            entity_rect.height
        )
    
    def apply_point(self, x, y):
        """Применить смещение камеры к точке"""
        return (x - self.rect.x, y - self.rect.y)
    
    def apply_rect(self, rect):
        """Применить смещение камеры к прямоугольнику"""
        return pygame.Rect(
            rect.x - self.rect.x,
            rect.y - self.rect.y,
            rect.width,
            rect.height
        ) 