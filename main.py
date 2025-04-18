import pygame
import random
from settings import *
from player import Player
from maze import Maze


def main():
    pygame.init()
    screen = pygame.display.set_mode((MAZE_WIDTH * CELL_SIZE, MAZE_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Light Guardian")
    clock = pygame.time.Clock()
    
    # Создаем лабиринт первым
    maze = Maze()
    player = Player(maze)  # Передаем лабиринт для корректного спавна
    
    font = pygame.font.SysFont('Arial', 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    maze = Maze()
                    player = Player(maze)
        
        player.handle_input(maze)
        
        screen.fill(BLACK)
        maze.draw(screen)
        player.draw(screen)
        
        # Интерфейс
        battery_status = "Фонарик выключен" if player.light.battery <= 0 else f"Заряд: {int(player.light.battery)}%"
        battery_text = font.render(battery_status, True, WHITE)
        screen.blit(battery_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()