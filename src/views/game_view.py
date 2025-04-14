import pygame


class GameView:
    def __init__(self):
        self.bg_color = (0, 0, 0)  # Черный фон
    
    def render(self, screen, player):
        screen.fill(self.bg_color)
        # Рисуем игрока (красный круг)
        pygame.draw.circle(screen, (255, 0, 0), (int(player.x), int(player.y)), player.radius)