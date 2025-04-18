import pygame
import random
from settings import *


class Maze:
    def __init__(self):
        self.walls = []
        self.generate_maze()

    def generate_maze(self):
        # 1. Инициализация: все ячейки - стены
        grid = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        
        # 2. Выбираем стартовую ячейку
        x, y = random.randint(0, MAZE_WIDTH-1), random.randint(0, MAZE_HEIGHT-1)
        grid[y][x] = 0  # 0 = проход, 1 = стена
        
        # 3. Алгоритм Recursive Backtracking
        stack = [(x, y)]
        while stack:
            x, y = stack[-1]
            directions = self._get_valid_directions(x, y, grid)
            
            if not directions:
                stack.pop()
                continue
                
            dx, dy = random.choice(directions)
            nx, ny = x + dx*2, y + dy*2  # Пропускаем одну ячейку
            
            grid[ny][nx] = 0
            grid[y + dy][x + dx] = 0  # Убираем стену между ячейками
            stack.append((nx, ny))
        
        # 4. Преобразуем в прямоугольники для Pygame
        self._convert_to_walls(grid)

    def _get_valid_directions(self, x, y, grid):
        directions = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx*2, y + dy*2
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and grid[ny][nx] == 1:
                directions.append((dx, dy))
        return directions

    def _convert_to_walls(self, grid):
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if grid[y][x] == 1:
                    self.walls.append(pygame.Rect(
                        x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                    ))

    def check_collision(self, rect):
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)