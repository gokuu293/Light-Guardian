import pygame
import random
import math
from settings import *
from entities.enemy import ShadowEnemy, GhostEnemy

class EnemyManager:
    """Класс для управления врагами: создание, удаление, обновление"""
    
    def __init__(self):
        self.enemies = []
        self.shadow_spawn_timer = 0
        self.ghost_spawn_timer = 0
        self.max_shadows = 5
        self.max_ghosts = 3
        self.shadow_spawn_interval = 600  # 10 секунд
        self.ghost_spawn_interval = 900   # 15 секунд
        self.initial_spawn_done = False   # Флаг для отслеживания начального спавна
        
        # Настройки спавна относительно игрока
        self.min_spawn_distance = 300     # Минимальное расстояние от игрока
        self.max_spawn_distance = 800     # Максимальное расстояние от игрока
    
    def update(self, player, level):
        """Обновление всех врагов и управление спавном"""
        # Начальный спавн врагов при первом обновлении
        if not self.initial_spawn_done:
            self._initial_spawn(player, level)
            self.initial_spawn_done = True
        
        # Обновляем существующих врагов
        for enemy in self.enemies:
            enemy.update(player, level, player.flashlight.on)
        
        # Проверяем столкновения с игроком
        for enemy in self.enemies:
            if enemy.visible and player.rect.colliderect(enemy.rect):
                return "game_over"
        
        # Удаляем невидимых теневых врагов из списка
        self.enemies = [enemy for enemy in self.enemies if not (isinstance(enemy, ShadowEnemy) and not enemy.visible)]
        
        # Управляем спавном новых врагов
        self._manage_spawning(player, level)
        
        return None
    
    def _initial_spawn(self, player, level):
        """Создает начальных врагов при старте уровня"""
        # Создаем 2 теневых и 1 призрачного врага
        for _ in range(2):
            self._spawn_enemy_at_distance("shadow", player, level)
        
        self._spawn_enemy_at_distance("ghost", player, level)
    
    def _manage_spawning(self, player, level):
        """Управление спавном врагов"""
        # Подсчет текущего количества врагов каждого типа
        shadow_count = sum(1 for enemy in self.enemies if isinstance(enemy, ShadowEnemy))
        ghost_count = sum(1 for enemy in self.enemies if isinstance(enemy, GhostEnemy))
        
        # Спавн теневых врагов
        if shadow_count < self.max_shadows:
            self.shadow_spawn_timer += 1
            if self.shadow_spawn_timer >= self.shadow_spawn_interval:
                self._spawn_enemy_at_distance("shadow", player, level)
                self.shadow_spawn_timer = 0
        
        # Спавн призрачных врагов
        if ghost_count < self.max_ghosts:
            self.ghost_spawn_timer += 1
            if self.ghost_spawn_timer >= self.ghost_spawn_interval:
                self._spawn_enemy_at_distance("ghost", player, level)
                self.ghost_spawn_timer = 0
    
    def _spawn_enemy_at_distance(self, enemy_type, player, level):
        """Создает врага на определенном расстоянии от игрока"""
        max_attempts = 50  # Максимальное количество попыток найти подходящее место
        
        for _ in range(max_attempts):
            # Генерируем случайный угол
            angle = random.uniform(0, 2 * math.pi)
            
            # Генерируем случайное расстояние в заданном диапазоне
            distance = random.uniform(self.min_spawn_distance, self.max_spawn_distance)
            
            # Вычисляем координаты
            x = player.rect.centerx + math.cos(angle) * distance
            y = player.rect.centery + math.sin(angle) * distance
            
            # Проверяем, не выходит ли за границы карты
            if x < 50 or x > MAP_WIDTH - 50 or y < 50 or y > MAP_HEIGHT - 50:
                continue
            
            # Создаем временный прямоугольник для проверки коллизий
            test_rect = pygame.Rect(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2, ENEMY_SIZE, ENEMY_SIZE)
            
            # Проверяем коллизии со стенами
            wall_collision = False
            for wall in level.walls:
                if test_rect.colliderect(wall):
                    wall_collision = True
                    break
            
            if not wall_collision:
                # Создаем врага нужного типа
                if enemy_type == "shadow":
                    self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                elif enemy_type == "ghost":
                    self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                return True
        
        # Если не удалось найти подходящее место, используем старый метод
        return self._fallback_spawn(enemy_type, level)
    
    def _fallback_spawn(self, enemy_type, level):
        """Запасной метод спавна, если не удалось разместить врага относительно игрока"""
        # Пытаемся найти подходящее место для спавна
        for _ in range(20):  # Максимум 20 попыток
            x = random.randint(100, MAP_WIDTH - 100)
            y = random.randint(100, MAP_HEIGHT - 100)
            
            # Создаем временный прямоугольник для проверки коллизий
            test_rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
            
            # Проверяем коллизии со стенами
            wall_collision = False
            for wall in level.walls:
                if test_rect.colliderect(wall):
                    wall_collision = True
                    break
            
            if not wall_collision:
                # Создаем врага нужного типа
                if enemy_type == "shadow":
                    self.enemies.append(ShadowEnemy(x, y))
                elif enemy_type == "ghost":
                    self.enemies.append(GhostEnemy(x, y))
                return True
        
        return False
    
    def draw(self, screen, camera):
        """Отрисовка всех врагов"""
        for enemy in self.enemies:
            enemy.draw(screen, camera)
    
    def reset(self):
        """Сброс всех врагов"""
        self.enemies.clear()
        self.shadow_spawn_timer = 0
        self.ghost_spawn_timer = 0
        self.initial_spawn_done = False 