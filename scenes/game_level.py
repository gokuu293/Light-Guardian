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
        self.game_state = "playing"  # playing, game_over, level_complete
        self.message_timer = 0

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_r and self.game_state == "game_over":
                    self.__init__()  # Перезапуск уровня
                if event.key == pygame.K_SPACE and self.game_state == "level_complete":
                    return "menu"  # Временно возвращаемся в меню
                    
        if self.game_state == "playing":
            self.player.handle_input(events, self.level)
        return None

    def update(self):
        if self.game_state == "playing":
            level_result = self.level.update(self.player)
            
            if level_result == "game_over":
                self.game_state = "game_over"
                self.message_timer = 180  # 3 секунды
            elif level_result == "level_complete":
                self.game_state = "level_complete"
                self.message_timer = 180
        else:
            if self.message_timer > 0:
                self.message_timer -= 1

    def draw(self, screen):
        screen.fill(BLACK)
        
        # Отрисовка уровня и игрока
        self.level.draw(screen)
        self.player.draw(screen)

        # Отрисовка заряда батареи
        battery_text = self.font.render(
            f"Battery: {int(self.player.flashlight.battery)}%", 
            True, 
            WHITE
        )
        screen.blit(battery_text, (10, 10))
        
        # Отрисовка сообщений о состоянии игры
        if self.game_state == "game_over":
            self.draw_message(screen, "GAME OVER", "Press R to restart")
        elif self.game_state == "level_complete":
            self.draw_message(screen, "LEVEL COMPLETE!", "Press SPACE to continue")
            
    def draw_message(self, screen, title, subtitle):
        # Затемнение экрана
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Отрисовка заголовка
        title_font = pygame.font.SysFont('Arial', 64)
        title_text = title_font.render(title, True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Отрисовка подзаголовка
        subtitle_text = self.font.render(subtitle, True, WHITE)
        screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, SCREEN_HEIGHT//2 + 20)) 