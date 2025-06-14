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
        in_light = self.is_in_light(player)
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
        
        new_rect = self.rect.copy()
        new_rect.x += dx
        new_rect.y += dy
        
        if not self.check_collision(new_rect, level):
            self.rect = new_rect
    
    def idle_movement(self, level):
        self.idle_timer += 1
        if self.idle_timer >= self.idle_duration:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.idle_timer = 0
            self.idle_duration = random.randint(60, 120)
        
        dx, dy = self.direction
        new_rect = self.rect.copy()
        new_rect.x += dx * self.speed / 2
        new_rect.y += dy * self.speed / 2
        
        if not self.check_collision(new_rect, level):
            self.rect = new_rect
        else:
            self.direction = (-dx, -dy)  # Разворот при столкновении
    
    def check_collision(self, rect, level):
        for wall in level.walls:
            if rect.colliderect(wall):
                return True
        return False
    
    def is_in_light(self, player):
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
        
        return angle_diff <= math.radians(LIGHT_ANGLE / 2)
    
    def draw(self, screen):
        color = ENEMY_COLOR
        if self.state == "stunned":
            color = ENEMY_STUNNED_COLOR
        pygame.draw.rect(screen, color, self.rect) 