import pygame
import math
from settings import *
from entities.lighting import Flashlight


class Player:
    def __init__(self, x=100, y=100):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.flashlight = Flashlight(self.rect.centerx, self.rect.centery)
        
        # Направление движения игрока (для анимации)
        self.direction = "right"  # right, left, up, down
        self.moving = False
        self.animation_timer = 0
        self.animation_speed = 8  # Меняем кадр каждые 8 обновлений
        self.animation_frame = 0
        
        # Загружаем базовый спрайт игрока
        self.base_sprite = pygame.image.load("assets/sprites/player/tile_0097.png").convert_alpha()
        sprite_size = int(PLAYER_SIZE * 2.2)
        self.base_sprite = pygame.transform.scale(self.base_sprite, (sprite_size, sprite_size))
        
        # Создаём словарь спрайтов для разных направлений
        self.sprites = {
            "right": self.base_sprite,
            "left": pygame.transform.flip(self.base_sprite, True, False),  # Отражаем по горизонтали
            "up": self.base_sprite, 
            "down": self.base_sprite
        }
        
        # Создаём анимацию движения для каждого направления
        self.animation_frames = {
            "right": [self.sprites["right"], self._create_movement_frame(self.sprites["right"])],
            "left": [self.sprites["left"], self._create_movement_frame(self.sprites["left"])],
            "up": [self.sprites["up"], self._create_movement_frame(self.sprites["up"])],
            "down": [self.sprites["down"], self._create_movement_frame(self.sprites["down"])]
        }
        
        # Корректируем смещение для центрирования спрайта
        self.sprite_size = sprite_size
        self.sprite_offset_x = (sprite_size - PLAYER_SIZE) // 2
        self.sprite_offset_y = (sprite_size - PLAYER_SIZE) // 2
    
    def _create_movement_frame(self, base_frame):
        """Создаёт второй кадр анимации на основе базового"""
        # Для простой анимации - слегка поворачиваем спрайт
        frame = pygame.transform.rotate(base_frame, 5)  # Поворот на 5 градусов
        # Центрируем повёрнутый спрайт
        return frame

    def handle_input(self, events, level, camera):
        keys = pygame.key.get_pressed()
        
        # Получаем позицию мыши и преобразуем с учетом камеры
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0] + camera.rect.x
        mouse_y = mouse_pos[1] + camera.rect.y
        
        # Обновление фонарика
        self.flashlight.update(mouse_x, mouse_y, self.rect.centerx, self.rect.centery)
        
        # Движение игрока
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        
        # Определяем направление движения для анимации
        self.moving = dx != 0 or dy != 0
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy < 0:  # Если движемся только вверх
            self.direction = "up"
        elif dy > 0:  # Если движемся только вниз
            self.direction = "down"
        
        # Обновляем анимацию если игрок движется
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames[self.direction])
        else:
            # Если игрок стоит, используем базовый кадр
            self.animation_frame = 0
        
        # Проверяем движение по осям отдельно для предотвращения "застревания" в стенах
        if dx != 0:
            new_rect = self.rect.copy()
            new_rect.x += dx
            if not self.check_collision(new_rect, level):
                self.rect.x = new_rect.x
        
        if dy != 0:
            new_rect = self.rect.copy()
            new_rect.y += dy
            if not self.check_collision(new_rect, level):
                self.rect.y = new_rect.y

    def check_collision(self, rect, level):
        for wall in level.walls:
            if rect.colliderect(wall):
                return True
        return False

    def draw(self, screen, camera, level):
        # Отрисовка игрока со спрайтом с учетом камеры
        player_rect = camera.apply(self.rect)
        
        # Выбираем текущий кадр анимации
        current_sprite = self.animation_frames[self.direction][self.animation_frame]
        
        # Получаем размеры текущего спрайта
        sprite_width, sprite_height = current_sprite.get_size()
        
        # Применяем смещение для центрирования спрайта
        sprite_rect = pygame.Rect(
            player_rect.x - self.sprite_offset_x,
            player_rect.y - self.sprite_offset_y,
            player_rect.width + self.sprite_offset_x * 2,
            player_rect.height + self.sprite_offset_y * 2
        )
        
        # Отрисовываем спрайт
        screen.blit(current_sprite, sprite_rect)
        
        # Отрисовка фонарика с учетом камеры
        self.flashlight.draw(screen, camera, level)