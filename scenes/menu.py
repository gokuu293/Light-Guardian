import pygame
from settings import *


class MainMenu:
    def __init__(self):
        self.font_large = pygame.font.SysFont('Arial', 64)
        self.font_small = pygame.font.SysFont('Arial', 32)
        self.selected = 0
        self.options = ["Start Game", "Settings", "Exit"]
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "start_game"
                    elif self.selected == 2:
                        return "exit"
        return None
    
    def update(self):
        pass
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        title = self.font_large.render("LIGHT GUARDIAN", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        for i, option in enumerate(self.options):
            color = (255, 200, 0) if i == self.selected else WHITE
            text = self.font_small.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300 + i*50))