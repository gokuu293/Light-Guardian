import pygame


class InputController:
    def handle(self, player):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]: player.y -= player.speed
        if keys[pygame.K_s]: player.y += player.speed
        if keys[pygame.K_a]: player.x -= player.speed
        if keys[pygame.K_d]: player.x += player.speed
        
        # Ограничение движения в пределах экрана
        player.x = max(player.radius, min(800 - player.radius, player.x))
        player.y = max(player.radius, min(600 - player.radius, player.y))