import pygame
import sys
from scenes.menu import MainMenu
from scenes.game_level import GameLevel
from scenes.controls import ControlsScene
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
        "game": GameLevel(),
        "controls": ControlsScene()  # Добавляем новую сцену
    }
    current_scene = "menu"
    previous_scene = None  # Сохраняем предыдущую сцену
    came_from_pause = False  # Флаг для отслеживания, пришли ли из паузы
    
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
        if scene_result:
            if scene_result == "start_game":
                previous_scene = current_scene
                current_scene = "game"
                # При переходе в игру, создаем новый экземпляр GameLevel
                scenes["game"] = GameLevel()
            elif scene_result == "exit":
                running = False
            elif scene_result == "menu":
                previous_scene = current_scene
                current_scene = "menu"
            elif scene_result == "controls":
                if current_scene == "game":
                    # Запоминаем, что пришли с экрана игры (с паузы)
                    came_from_pause = True
                previous_scene = current_scene
                current_scene = "controls"
            elif scene_result == "back_from_controls":
                if came_from_pause:
                    # Если пришли с паузы, возвращаемся в игру
                    current_scene = "game"
                    came_from_pause = False
                else:
                    # Иначе возвращаемся в меню
                    current_scene = "menu"
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()