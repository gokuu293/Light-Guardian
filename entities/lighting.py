import pygame
import math
from settings import *


class Flashlight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.battery = 100
        self.on = True
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def update(self, mouse_x, mouse_y, player_x, player_y):
        self.x = player_x
        self.y = player_y
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        self.angle = math.atan2(dy, dx)
        
        if self.on:
            self.battery = max(0, self.battery - LIGHT_DRAIN)

    def draw(self, screen):
        if not self.on or self.battery <= 0:
            return
            
        self.light_surface.fill((0, 0, 0, 0))
        angle_rad = math.radians(LIGHT_ANGLE)
        distance = LIGHT_RADIUS * (self.battery / 100)
        
        points = [
            (self.x, self.y),
            (
                self.x + distance * math.cos(self.angle - angle_rad/2),
                self.y + distance * math.sin(self.angle - angle_rad/2)
            ),
            (
                self.x + distance * math.cos(self.angle + angle_rad/2),
                self.y + distance * math.sin(self.angle + angle_rad/2)
            )
        ]
        
        pygame.draw.polygon(self.light_surface, LIGHT_AMBER, points)
        screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def get_current_radius(self):
        return LIGHT_RADIUS * (self.battery / 100)