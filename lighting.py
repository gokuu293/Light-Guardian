import pygame
from settings import *


class LightSource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = LIGHT_RADIUS
        self.battery = 100  # Заряд фонарика
        self.light_surface = self._create_light_surface()

    def _create_light_surface(self):
        surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, LIGHT_COLOR, (self.radius, self.radius), self.radius)
        return surface

    def update_pos(self, x, y):
        self.x = x
        self.y = y
        self.battery = max(0, self.battery - LIGHT_DRAIN_RATE)  # Не опускается ниже 0

    def draw(self, screen):
        if self.battery > 0:
            screen.blit(self.light_surface, (self.x - self.radius, self.y - self.radius))