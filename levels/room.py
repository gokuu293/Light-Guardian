import pygame
import random
import math
from settings import *

class Room:
    def __init__(self, x, y, width, height, room_type="normal"):
        # Убеждаемся, что комната не слишком маленькая
        min_width = 200
        min_height = 200
        self.rect = pygame.Rect(x, y, max(width, min_width), max(height, min_height))
        self.type = room_type  # "start", "normal", "difficult", "exit"
        self.walls = []
        self.doors = []  # Точки соединения с другими комнатами
        self.obstacles = []  # Внутренние препятствия
        self.batteries = []  # Батарейки в комнате
        self.enemy_spawn_points = []  # Места для спавна врагов
        
        # Создаем стены комнаты
        self._create_walls()
        
        # Безопасная зона в центре комнаты (особенно для стартовой комнаты)
        self.safe_zone = pygame.Rect(
            self.rect.centerx - PLAYER_SIZE * 3,
            self.rect.centery - PLAYER_SIZE * 3,
            PLAYER_SIZE * 6,
            PLAYER_SIZE * 6
        )
        
        # Генерируем внутренние препятствия в зависимости от типа комнаты
        self._generate_obstacles()
        
    def _create_walls(self):
        # Создаем 4 стены для комнаты
        self.walls = [
            # Верхняя стена
            pygame.Rect(self.rect.x, self.rect.y, self.rect.width, WALL_THICKNESS),
            # Левая стена
            pygame.Rect(self.rect.x, self.rect.y, WALL_THICKNESS, self.rect.height),
            # Правая стена
            pygame.Rect(self.rect.x + self.rect.width - WALL_THICKNESS, self.rect.y, 
                      WALL_THICKNESS, self.rect.height),
            # Нижняя стена
            pygame.Rect(self.rect.x, self.rect.y + self.rect.height - WALL_THICKNESS, 
                      self.rect.width, WALL_THICKNESS)
        ]
    
    def _generate_obstacles(self):
        # Уменьшаем количество препятствий в 1.5 раза
        # Было: obstacle_count = int((self.rect.width * self.rect.height) / 25000)
        obstacle_count = int((self.rect.width * self.rect.height) / 37500)  # Делитель увеличен
        
        if self.type == "difficult":
            obstacle_count = int(obstacle_count * 1.3)  # Было 1.5
        elif self.type == "start":
            obstacle_count = int(obstacle_count * 0.3)  # Значительно меньше препятствий в стартовой комнате
        elif self.type == "exit":
            obstacle_count = int(obstacle_count * 0.4)  # Было 0.5
        
        # Минимальный отступ от стен увеличен
        padding = WALL_THICKNESS + 40  # Было 30
        
        # Создаем случайные препятствия
        for _ in range(obstacle_count):
            # Размер препятствия
            size = random.randint(30, 50)
            
            # Случайная позиция внутри комнаты (с отступом от стен)
            for attempt in range(20):  # Ограничиваем количество попыток
                x = random.randint(self.rect.x + padding, self.rect.x + self.rect.width - padding - size)
                y = random.randint(self.rect.y + padding, self.rect.y + self.rect.height - padding - size)
                
                obstacle = pygame.Rect(x, y, size, size)
                
                # Не размещаем препятствия в безопасной зоне стартовой комнаты
                if self.type == "start" and obstacle.colliderect(self.safe_zone):
                    continue
                
                # Увеличенный отступ между препятствиями для более свободного пространства
                extra_space = 15  # Дополнительный отступ между препятствиями
                obstacle_check = pygame.Rect(
                    obstacle.x - extra_space, 
                    obstacle.y - extra_space, 
                    obstacle.width + extra_space*2, 
                    obstacle.height + extra_space*2
                )
                
                # Проверяем, не перекрывает ли препятствие другие объекты
                if not self._check_collision(obstacle_check):
                    self.obstacles.append(obstacle)
                    
                    # Добавляем места для спавна врагов рядом с препятствиями (но не в стартовой комнате)
                    # Уменьшаем вероятность спавна врагов
                    if self.type != "start" and self.type != "exit":
                        spawn_chance = 0.4 if self.type == "difficult" else 0.2  # Было 0.3 для normal
                        if random.random() < spawn_chance:
                            # Увеличиваем минимальное расстояние для спавна врагов от препятствий
                            min_dist = 85  # Было 70
                            max_dist = 150  # Было 120
                            
                            # Создаем несколько попыток найти подходящее место для спавна
                            for spawn_attempt in range(10):
                                # Получаем точку на определенном расстоянии от препятствия
                                angle = random.uniform(0, 2 * 3.14159)  # Случайный угол
                                dist = random.randint(min_dist, max_dist)  # Расстояние от препятствия
                                spawn_x = x + size/2 + math.cos(angle) * dist
                                spawn_y = y + size/2 + math.sin(angle) * dist
                                
                                # Убедимся, что точка спавна внутри комнаты с большим отступом от стен
                                safe_padding = padding + 10
                                if (spawn_x < self.rect.x + safe_padding or 
                                    spawn_x > self.rect.x + self.rect.width - safe_padding or
                                    spawn_y < self.rect.y + safe_padding or 
                                    spawn_y > self.rect.y + self.rect.height - safe_padding):
                                    continue
                                
                                # Создаем временный прямоугольник для проверки коллизий
                                # с дополнительным буфером для безопасности
                                safety_margin = 15  # Увеличиваем с 10 до 15
                                test_rect = pygame.Rect(
                                    spawn_x - ENEMY_SIZE/2 - safety_margin, 
                                    spawn_y - ENEMY_SIZE/2 - safety_margin, 
                                    ENEMY_SIZE + safety_margin*2, 
                                    ENEMY_SIZE + safety_margin*2
                                )
                                
                                if not self._check_collision(test_rect):
                                    # Вместо немедленного добавления точки спавна
                                    # Просто запоминаем кандидата, проверка с глобальными стенами будет в Level1._setup_enemies
                                    self.enemy_spawn_points.append((spawn_x, spawn_y))
                                    break  # Найдена подходящая точка спавна
                    
                    break  # Препятствие размещено, прерываем цикл попыток
    
    def can_add_door(self, direction):
        """Проверяет, можно ли добавить дверь в указанном направлении"""
        # Минимальное расстояние от угла комнаты до двери
        min_edge_distance = 100
        
        if direction == "top" or direction == "bottom":
            # Проверяем, достаточно ли широка комната
            return self.rect.width >= min_edge_distance * 2 + 60  # 60 - ширина двери
        elif direction == "left" or direction == "right":
            # Проверяем, достаточно ли высока комната
            return self.rect.height >= min_edge_distance * 2 + 60
        
        return False
    
    def add_door(self, direction, position=None):
        """Добавляет дверь в указанном направлении: 'top', 'right', 'bottom', 'left'"""
        if not self.can_add_door(direction):
            return False  # Нельзя добавить дверь в этом направлении
            
        door_width = 60  # Ширина двери
        door = None
        door_info = None
        
        if direction == "top":
            if position is None:
                position = random.randint(self.rect.x + 100, self.rect.x + self.rect.width - 100 - door_width)
            door = pygame.Rect(position, self.rect.y, door_width, WALL_THICKNESS)
            door_info = {"rect": door, "direction": direction, "position": position}
            
        elif direction == "right":
            if position is None:
                position = random.randint(self.rect.y + 100, self.rect.y + self.rect.height - 100 - door_width)
            door = pygame.Rect(self.rect.x + self.rect.width - WALL_THICKNESS, position, 
                             WALL_THICKNESS, door_width)
            door_info = {"rect": door, "direction": direction, "position": position}
            
        elif direction == "bottom":
            if position is None:
                position = random.randint(self.rect.x + 100, self.rect.x + self.rect.width - 100 - door_width)
            door = pygame.Rect(position, self.rect.y + self.rect.height - WALL_THICKNESS, 
                             door_width, WALL_THICKNESS)
            door_info = {"rect": door, "direction": direction, "position": position}
            
        elif direction == "left":
            if position is None:
                position = random.randint(self.rect.y + 100, self.rect.y + self.rect.height - 100 - door_width)
            door = pygame.Rect(self.rect.x, position, WALL_THICKNESS, door_width)
            door_info = {"rect": door, "direction": direction, "position": position}
        
        # Проверяем, не перекрывает ли дверь существующие двери
        for existing_door in self.doors:
            if door.colliderect(existing_door["rect"]):
                return False  # Перекрытие, не добавляем дверь
        
        # Добавляем дверь
        self.doors.append(door_info)
        return True
    
    def add_battery(self, count=1):
        """Добавляет батарейки в комнату"""
        padding = WALL_THICKNESS + 30
        batteries_added = 0
        max_attempts = 50
        
        while batteries_added < count and max_attempts > 0:
            x = random.randint(self.rect.x + padding, self.rect.x + self.rect.width - padding - BATTERY_SIZE)
            y = random.randint(self.rect.y + padding, self.rect.y + self.rect.height - padding - BATTERY_SIZE)
            
            battery = pygame.Rect(x, y, BATTERY_SIZE, BATTERY_SIZE)
            
            # Избегаем размещения батареек в безопасной зоне стартовой комнаты
            if self.type == "start" and battery.colliderect(self.safe_zone):
                max_attempts -= 1
                continue
                
            # Проверяем коллизии
            if not self._check_collision(battery):
                self.batteries.append(battery)
                batteries_added += 1
            else:
                max_attempts -= 1
    
    def _check_collision(self, rect):
        """Проверяет коллизии с существующими объектами в комнате"""
        # Проверка коллизий со стенами
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        
        # Проверка коллизий с дверями
        for door in self.doors:
            if rect.colliderect(door["rect"]):
                return True
        
        # Проверка коллизий с препятствиями
        for obstacle in self.obstacles:
            if rect.colliderect(obstacle):
                return True
        
        # Проверка коллизий с батарейками
        for battery in self.batteries:
            if rect.colliderect(battery):
                return True
        
        return False

    def get_center(self):
        """Возвращает центр комнаты"""
        return (self.rect.centerx, self.rect.centery)