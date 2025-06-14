import pygame
import random
from settings import *
from entities.enemy import Enemy


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
        
        # Батарейки для пополнения заряда
        self.batteries = [
            pygame.Rect(350, 150, 20, 20),
            pygame.Rect(600, 450, 20, 20),
            pygame.Rect(200, 500, 20, 20),
            pygame.Rect(800, 200, 20, 20)
        ]
        
        # Враги
        self.enemies = [
            Enemy(500, 200),
            Enemy(700, 500),
            Enemy(300, 400)
        ]
        
        self.exit = pygame.Rect(SCREEN_WIDTH-50, SCREEN_HEIGHT-50, 40, 40)

    def update(self, player):
        # Обновление врагов
        for enemy in self.enemies:
            enemy.update(player, self, player.flashlight.on)
        
        # Проверка сбора батареек
        for battery in self.batteries[:]:
            if player.rect.colliderect(battery):
                player.flashlight.battery = min(100, player.flashlight.battery + 25)
                self.batteries.remove(battery)
        
        # Проверка столкновения с врагами
        for enemy in self.enemies:
            if player.rect.colliderect(enemy.rect) and enemy.state != "stunned":
                return "game_over"
                
        # Проверка достижения выхода
        if player.rect.colliderect(self.exit):
            return "level_complete"
            
        return None

    def draw(self, screen):
        # Стены
        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)
        
        # Батарейки
        for battery in self.batteries:
            pygame.draw.rect(screen, (0, 255, 0), battery)
        
        # Враги
        for enemy in self.enemies:
            enemy.draw(screen)
        
        # Выход
        pygame.draw.rect(screen, (255, 0, 0), self.exit)