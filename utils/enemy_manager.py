import pygame
import random
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
    
    def update(self, player, level):
        """Обновление всех врагов и управление спавном"""
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
        self._manage_spawning(level)
        
        return None
    
    def _manage_spawning(self, level):
        """Управление спавном врагов"""
        # Подсчет текущего количества врагов каждого типа
        shadow_count = sum(1 for enemy in self.enemies if isinstance(enemy, ShadowEnemy))
        ghost_count = sum(1 for enemy in self.enemies if isinstance(enemy, GhostEnemy))
        
        # Спавн теневых врагов
        if shadow_count < self.max_shadows:
            self.shadow_spawn_timer += 1
            if self.shadow_spawn_timer >= self.shadow_spawn_interval:
                self._spawn_enemy("shadow", level)
                self.shadow_spawn_timer = 0
        
        # Спавн призрачных врагов
        if ghost_count < self.max_ghosts:
            self.ghost_spawn_timer += 1
            if self.ghost_spawn_timer >= self.ghost_spawn_interval:
                self._spawn_enemy("ghost", level)
                self.ghost_spawn_timer = 0
    
    def _spawn_enemy(self, enemy_type, level):
        """Создание нового врага указанного типа"""
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
                break
    
    def draw(self, screen, camera):
        """Отрисовка всех врагов"""
        for enemy in self.enemies:
            enemy.draw(screen, camera)
    
    def reset(self):
        """Сброс всех врагов"""
        self.enemies.clear()
        self.shadow_spawn_timer = 0
        self.ghost_spawn_timer = 0 