import pygame
from settings import *
from entities.lighting import Flashlight


class Player:
    def __init__(self, x=100, y=100):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.flashlight = Flashlight(self.rect.centerx, self.rect.centery)

    def handle_input(self, events, level, camera):
        keys = pygame.key.get_pressed()
        
        # Получаем позицию мыши и преобразуем с учетом камеры
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0] + camera.rect.x
        mouse_y = mouse_pos[1] + camera.rect.y
        
        # Обновление фонарика
        self.flashlight.update(mouse_x, mouse_y, self.rect.centerx, self.rect.centery)
        
        # Движение игрока
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        
        # Проверяем движение по осям отдельно для предотвращения "застревания" в стенах
        if dx != 0:
            new_rect = self.rect.copy()
            new_rect.x += dx
            if not self.check_collision(new_rect, level):
                self.rect.x = new_rect.x
        
        if dy != 0:
            new_rect = self.rect.copy()
            new_rect.y += dy
            if not self.check_collision(new_rect, level):
                self.rect.y = new_rect.y

    def check_collision(self, rect, level):
        for wall in level.walls:
            if rect.colliderect(wall):
                return True
        return False

    def draw(self, screen, camera, level):
        # Отрисовка игрока с учетом камеры
        player_rect = camera.apply(self.rect)
        pygame.draw.rect(screen, WHITE, player_rect)
        
        # Отрисовка фонарика с учетом камеры
        self.flashlight.draw(screen, camera, level)