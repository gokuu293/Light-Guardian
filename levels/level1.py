import pygame
import random
from settings import *
from utils.enemy_manager import EnemyManager


class Level1:
    def __init__(self):
        # Создаем большую карту подземелья
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        
        # Внешние стены
        self.walls = [
            # Внешние границы
            pygame.Rect(0, 0, self.width, WALL_THICKNESS),  # Верх
            pygame.Rect(0, 0, WALL_THICKNESS, self.height),  # Лево
            pygame.Rect(0, self.height-WALL_THICKNESS, self.width, WALL_THICKNESS),  # Низ
            pygame.Rect(self.width-WALL_THICKNESS, 0, WALL_THICKNESS, self.height),  # Право
        ]
        
        # Добавляем стены для создания подземелья
        self._create_dungeon_walls()
        
        # Батарейки для пополнения заряда
        self.batteries = [
            pygame.Rect(350, 150, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(600, 450, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(200, 500, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(800, 200, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(1200, 300, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(1500, 600, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(1800, 400, BATTERY_SIZE, BATTERY_SIZE),
            pygame.Rect(2000, 800, BATTERY_SIZE, BATTERY_SIZE),
        ]
        
        # Менеджер врагов
        self.enemy_manager = EnemyManager()
        
        # Выход с уровня
        self.exit = pygame.Rect(self.width-100, self.height-100, EXIT_SIZE, EXIT_SIZE)
    
    def _create_dungeon_walls(self):
        # Основные коридоры и комнаты подземелья
        
        # Центральный зал
        central_hall = pygame.Rect(800, 500, 400, 300)
        
        # Коридоры
        corridors = [
            # Горизонтальные коридоры
            pygame.Rect(300, 300, 500, WALL_THICKNESS*2),
            pygame.Rect(1200, 600, 600, WALL_THICKNESS*2),
            pygame.Rect(600, 900, 800, WALL_THICKNESS*2),
            
            # Вертикальные коридоры
            pygame.Rect(500, 300, WALL_THICKNESS*2, 600),
            pygame.Rect(1000, 200, WALL_THICKNESS*2, 700),
            pygame.Rect(1500, 400, WALL_THICKNESS*2, 500),
        ]
        
        # Комнаты
        rooms = [
            # Верхние комнаты
            pygame.Rect(300, 100, 200, 200),
            pygame.Rect(700, 150, 250, 150),
            pygame.Rect(1200, 200, 300, 200),
            pygame.Rect(1800, 100, 350, 250),
            
            # Нижние комнаты
            pygame.Rect(200, 700, 250, 200),
            pygame.Rect(1300, 800, 200, 300),
            pygame.Rect(1800, 700, 400, 200),
        ]
        
        # Создаем стены для комнат и коридоров
        for room in rooms:
            # Верхняя стена
            self.walls.append(pygame.Rect(room.x, room.y, room.width, WALL_THICKNESS))
            # Левая стена
            self.walls.append(pygame.Rect(room.x, room.y, WALL_THICKNESS, room.height))
            # Правая стена
            self.walls.append(pygame.Rect(room.x + room.width - WALL_THICKNESS, room.y, WALL_THICKNESS, room.height))
            # Нижняя стена
            self.walls.append(pygame.Rect(room.x, room.y + room.height - WALL_THICKNESS, room.width, WALL_THICKNESS))
        
        # Добавляем случайные колонны и препятствия
        for _ in range(20):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            size = random.randint(30, 80)
            
            # Проверяем, не перекрывает ли новое препятствие существующие стены
            new_obstacle = pygame.Rect(x, y, size, size)
            overlap = False
            for wall in self.walls:
                if new_obstacle.colliderect(wall):
                    overlap = True
                    break
            
            if not overlap:
                self.walls.append(new_obstacle)

    def update(self, player):
        # Обновление врагов через менеджер
        enemy_result = self.enemy_manager.update(player, self)
        if enemy_result == "game_over":
            return "game_over"
        
        # Проверка сбора батареек
        for battery in self.batteries[:]:
            if player.rect.colliderect(battery):
                player.flashlight.battery = min(100, player.flashlight.battery + BATTERY_CHARGE)
                self.batteries.remove(battery)
                
        # Проверка достижения выхода
        if player.rect.colliderect(self.exit):
            return "level_complete"
            
        return None

    def draw(self, screen, camera):
        # Рисуем пол подземелья
        screen.fill(DUNGEON_FLOOR)
        
        # Стены - рисуем только те, что видны на экране
        for wall in self.walls:
            wall_rect = camera.apply(wall)
            # Проверяем, находится ли стена в пределах экрана
            if (wall_rect.right >= 0 and wall_rect.left <= SCREEN_WIDTH and 
                wall_rect.bottom >= 0 and wall_rect.top <= SCREEN_HEIGHT):
                pygame.draw.rect(screen, WALL_COLOR, wall_rect)
        
        # Батарейки - рисуем только видимые
        for battery in self.batteries:
            battery_rect = camera.apply(battery)
            if (battery_rect.right >= 0 and battery_rect.left <= SCREEN_WIDTH and 
                battery_rect.bottom >= 0 and battery_rect.top <= SCREEN_HEIGHT):
                pygame.draw.rect(screen, (0, 255, 0), battery_rect)
        
        # Отрисовка врагов через менеджер
        self.enemy_manager.draw(screen, camera)
        
        # Выход
        exit_rect = camera.apply(self.exit)
        if (exit_rect.right >= 0 and exit_rect.left <= SCREEN_WIDTH and 
            exit_rect.bottom >= 0 and exit_rect.top <= SCREEN_HEIGHT):
            pygame.draw.rect(screen, (255, 0, 0), exit_rect)