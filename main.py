import pygame
import sys
from scenes.menu import MainMenu
from scenes.game_level import GameLevel
from entities.player import Player
from settings import *


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Light Guardian")
    clock = pygame.time.Clock()
    
    # Сцены игры
    scenes = {
        "menu": MainMenu(),
        "game": GameLevel()
    }
    current_scene = "menu"
    
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Обновление текущей сцены
        scene_result = scenes[current_scene].handle_input(events)
        scenes[current_scene].update()
        scenes[current_scene].draw(screen)
        
        # Обработка переключения сцен
        if scene_result == "start_game":
            current_scene = "game"
        elif scene_result == "exit":
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()