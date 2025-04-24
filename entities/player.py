import pygame
from settings import *
from entities.lighting import Flashlight


class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.flashlight = Flashlight(self.rect.centerx, self.rect.centery)

    def handle_input(self, events, level):
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Обновление фонарика
        self.flashlight.update(mouse_x, mouse_y, self.rect.centerx, self.rect.centery)
        
        # Движение игрока
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        
        new_rect = self.rect.copy()
        new_rect.x += dx
        new_rect.y += dy
        
        if not self.check_collision(new_rect, level):
            self.rect = new_rect

    def check_collision(self, rect, level):
        for wall in level.walls:
            if rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        self.flashlight.draw(screen)