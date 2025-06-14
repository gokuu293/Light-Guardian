import pygame
import math
import random
from settings import *

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.speed = ENEMY_SPEED
        self.state = "idle"  # idle, chase, stunned
        self.stunned_timer = 0
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.idle_timer = 0
        self.idle_duration = random.randint(60, 120)  # 1-2 секунды при 60 FPS
        
    def update(self, player, level, flashlight_on):
        if self.state == "stunned":
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.state = "idle"
            return
        
        # Проверка, находится ли враг в свете фонарика
        in_light = self.is_in_light(player, level)
        if in_light and flashlight_on:
            self.state = "stunned"
            self.stunned_timer = ENEMY_STUN_TIME
            return
        
        # Определение состояния врага
        distance = math.sqrt((player.rect.centerx - self.rect.centerx)**2 + 
                            (player.rect.centery - self.rect.centery)**2)
        
        if distance < ENEMY_DETECTION_RADIUS and not flashlight_on:
            self.state = "chase"
        elif self.state == "chase" and distance > ENEMY_CHASE_LIMIT:
            self.state = "idle"
            
        # Движение в зависимости от состояния
        if self.state == "chase":
            self.chase_player(player, level)
        else:
            self.idle_movement(level)
    
    def chase_player(self, player, level):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
        
        # Проверяем движение по осям отдельно для предотвращения "застревания"
        new_rect_x = self.rect.copy()
        new_rect_x.x += dx
        
        new_rect_y = self.rect.copy()
        new_rect_y.y += dy
        
        if not self.check_collision(new_rect_x, level):
            self.rect.x = new_rect_x.x
            
        if not self.check_collision(new_rect_y, level):
            self.rect.y = new_rect_y.y
    
    def idle_movement(self, level):
        self.idle_timer += 1
        if self.idle_timer >= self.idle_duration:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.idle_timer = 0
            self.idle_duration = random.randint(60, 120)
        
        dx, dy = self.direction
        
        # Проверяем движение по осям отдельно
        new_rect_x = self.rect.copy()
        new_rect_x.x += dx * self.speed / 2
        
        new_rect_y = self.rect.copy()
        new_rect_y.y += dy * self.speed / 2
        
        if not self.check_collision(new_rect_x, level):
            self.rect.x = new_rect_x.x
        else:
            self.direction = (-dx, dy)  # Меняем направление по X
            
        if not self.check_collision(new_rect_y, level):
            self.rect.y = new_rect_y.y
        else:
            self.direction = (dx, -dy)  # Меняем направление по Y
    
    def check_collision(self, rect, level):
        for wall in level.walls:
            if rect.colliderect(wall):
                return True
        return False
    
    def is_in_light(self, player, level):
        # Проверка, находится ли враг в конусе света фонарика
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > player.flashlight.get_current_radius():
            return False
        
        # Угол между игроком и врагом
        angle = math.atan2(dy, dx)
        angle_diff = abs(angle - player.flashlight.angle)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        if angle_diff > math.radians(LIGHT_ANGLE / 2):
            return False
            
        # Проверка, нет ли препятствий между игроком и врагом
        # Используем алгоритм Брезенхема для проверки линии видимости
        return self.has_line_of_sight(player.rect.centerx, player.rect.centery, 
                                     self.rect.centerx, self.rect.centery, level.walls)
    
    def has_line_of_sight(self, x1, y1, x2, y2, walls):
        """Проверяет, есть ли прямая видимость между двумя точками"""
        # Алгоритм Брезенхема для проверки линии
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        check_rect = pygame.Rect(0, 0, 4, 4)
        
        while x1 != x2 or y1 != y2:
            check_rect.x = x1 - 2
            check_rect.y = y1 - 2
            
            for wall in walls:
                if wall.colliderect(check_rect):
                    return False
                    
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
                
        return True
    
    def draw(self, screen, camera):
        # Отрисовка врага с учетом камеры
        enemy_rect = camera.apply(self.rect)
        color = ENEMY_COLOR
        if self.state == "stunned":
            color = ENEMY_STUNNED_COLOR
        pygame.draw.rect(screen, color, enemy_rect) 