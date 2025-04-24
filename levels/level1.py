import pygame
from settings import *


class Level1:
    def __init__(self):
        self.walls = [
            # Внешние стены
            pygame.Rect(0, 0, SCREEN_WIDTH, WALL_THICKNESS),  # Верх
            pygame.Rect(0, 0, WALL_THICKNESS, SCREEN_HEIGHT),  # Лево
            pygame.Rect(0, SCREEN_HEIGHT-WALL_THICKNESS, SCREEN_WIDTH, WALL_THICKNESS),  # Низ
            pygame.Rect(SCREEN_WIDTH-WALL_THICKNESS, 0, WALL_THICKNESS, SCREEN_HEIGHT),  # Право
            
            # Комнаты и коридоры
            pygame.Rect(300, 100, WALL_THICKNESS, 300),  # Левая стена комнаты 1
            pygame.Rect(300, 100, 400, WALL_THICKNESS),   # Верх комнаты 1
            pygame.Rect(700, 100, WALL_THICKNESS, 300),   # Правая стена комнаты 1
            pygame.Rect(500, 300, 200, WALL_THICKNESS),   # Нижняя перегородка
            
            # Большая центральная комната
            pygame.Rect(400, 400, 400, WALL_THICKNESS),   # Верх центра
            pygame.Rect(400, 400, WALL_THICKNESS, 200),   # Лево центра
            pygame.Rect(800, 400, WALL_THICKNESS, 200),   # Право центра
        ]
        
        self.batteries = [
            pygame.Rect(350, 150, 20, 20),
            pygame.Rect(600, 450, 20, 20)
        ]
        
        self.exit = pygame.Rect(SCREEN_WIDTH-50, SCREEN_HEIGHT-50, 40, 40)

    def draw(self, screen):
        # Стены
        for wall in self.walls:
            pygame.draw.rect(screen, (30, 30, 30), wall)
        
        # Батарейки
        for battery in self.batteries:
            pygame.draw.rect(screen, (0, 255, 0), battery)
        
        # Выход
        pygame.draw.rect(screen, (255, 0, 0), self.exit)