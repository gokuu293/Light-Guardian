import pygame
import sys
from scenes.menu import MainMenu
from scenes.game_level import GameLevel
from scenes.controls import ControlsScene
from scenes.settings_scene import SettingsScene
from entities.player import Player
from utils.sound_manager import SoundManager
from settings import *


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Light Guardian")
    clock = pygame.time.Clock()
    
    # Инициализируем звуковой менеджер
    sound_manager = SoundManager()
    
    # Воспроизводим фоновую музыку меню
    sound_manager.play_menu_music()
    
    # Сцены игры
    scenes = {
        "menu": MainMenu(sound_manager),
        "game": GameLevel(sound_manager),
        "controls": ControlsScene(sound_manager),
        "settings": SettingsScene(sound_manager)
    }
    current_scene = "menu"
    previous_scene = None
    came_from_pause = False
    
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
                # Воспроизводим звук выбора и останавливаем музыку меню при переходе в игру
                sound_manager.play_sound("menu_select")
                sound_manager.stop_music()
                # При переходе в игру, создаем новый экземпляр GameLevel
                scenes["game"] = GameLevel(sound_manager)
            elif scene_result == "exit":
                running = False
            elif scene_result == "menu":
                previous_scene = current_scene
                current_scene = "menu"
                # Запускаем музыку меню при возврате из игры
                if previous_scene == "game":
                    sound_manager.play_menu_music()
            elif scene_result == "controls":
                sound_manager.play_sound("menu_select")
                if current_scene == "game":
                    # Запоминаем, что пришли с экрана игры (с паузы)
                    came_from_pause = True
                previous_scene = current_scene
                current_scene = "controls"
            elif scene_result == "settings":
                sound_manager.play_sound("menu_select")
                if current_scene == "game":
                    came_from_pause = True
                previous_scene = current_scene
                current_scene = "settings"
            elif scene_result == "back_from_controls":
                sound_manager.play_sound("menu_select")
                if came_from_pause:
                    # Если пришли с паузы, возвращаемся в игру
                    current_scene = "game"
                    came_from_pause = False
                else:
                    # Иначе возвращаемся в меню
                    current_scene = "menu"
            elif scene_result == "back_from_settings":
                sound_manager.play_sound("menu_select")
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