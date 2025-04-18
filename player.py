import pygame
import random
from settings import *
from lighting import LightSource


class Player:
    def __init__(self, maze):
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.light = LightSource(0, 0)
        
        # Генерация позиции вне стен
        self._find_valid_position(maze)
        
    def _find_valid_position(self, maze):
        # Находит случайную позицию не в стене
        max_attempts = 100
        for _ in range(max_attempts):
            self.rect.x = random.randint(0, MAZE_WIDTH * CELL_SIZE - self.rect.width)
            self.rect.y = random.randint(0, MAZE_HEIGHT * CELL_SIZE - self.rect.height)
            if not maze.check_collision(self.rect):
                self.light.update_pos(self.rect.centerx, self.rect.centery)
                return
        # Если не нашли - ставим в центр
        self.rect.center = (MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2)

    def handle_input(self, maze):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        
        # Временное перемещение
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        
        # Проверка границ и коллизий
        if (0 <= temp_rect.left and temp_rect.right <= MAZE_WIDTH * CELL_SIZE and
            0 <= temp_rect.top and temp_rect.bottom <= MAZE_HEIGHT * CELL_SIZE and
            not maze.check_collision(temp_rect)):
            self.rect = temp_rect
        
        self.light.update_pos(self.rect.centerx, self.rect.centery)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        self.light.draw(screen)