import pygame
from settings import *
from entities.player import Player
from levels.level1 import Level1


class GameLevel:
    def __init__(self):
        self.player = Player()
        self.level = Level1()
        self.walls = self.level.walls
        self.font = pygame.font.SysFont('Arial', 24)

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
        self.player.handle_input(events, self.level)
        return None

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)
        self.player.draw(screen)

        # Отрисовка заряда батареи
        battery_text = self.font.render(
            f"Battery: {int(self.player.flashlight.battery)}%", 
            True, 
            (255, 255, 255)  # Белый цвет
        )
        screen.blit(battery_text, (10, 10))  # Позиция в левом верхнем углу
        