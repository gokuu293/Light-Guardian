import pygame
from models.player import Player
from views.game_view import GameView
from controllers.input import InputController


def main():
    # Инициализация Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Light Guardian")
    clock = pygame.time.Clock()
    
    # Создание объектов
    player = Player()
    game_view = GameView()
    input_controller = InputController()
    
    # Главный игровой цикл
    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Обновление
        input_controller.handle(player)
        
        # Отрисовка
        game_view.render(screen, player)
        pygame.display.flip()
        
        # Ограничение FPS
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()