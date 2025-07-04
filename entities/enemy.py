import pygame
import math
import random
from settings import *
from abc import ABC, abstractmethod

class Enemy(ABC):
    """Базовый абстрактный класс для всех врагов"""
    
    def __init__(self, x, y, size, speed, color, sprite_path=None, sound_manager=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.color = color
        self.state = "idle"  # idle, chase, affected_by_light, fading
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.idle_timer = 0
        self.idle_duration = random.randint(60, 120)  # 1-2 секунды при 60 FPS
        self.effect_timer = 0
        self.visible = True
        
        # Загружаем спрайт, если путь предоставлен, с увеличенным размером
        self.sprite = None
        self.sprite_offset_x = 0
        self.sprite_offset_y = 0
        
        if sprite_path:
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
            # Увеличиваем размер спрайта (в 1.8 раза больше базового размера врага)
            sprite_size = int(size * 1.8)
            self.sprite = pygame.transform.scale(self.sprite, (sprite_size, sprite_size))
            
            # Сохраняем смещение для центрирования спрайта
            self.sprite_offset_x = (sprite_size - size) // 2
            self.sprite_offset_y = (sprite_size - size) // 2
        
        # Добавляем звуковой менеджер
        self.sound_manager = sound_manager
        
        # Флаг для отслеживания обнаружения игрока
        self.detected_player = False
        
        # Флаги для звуковых эффектов при попадании света
        self._light_hit_played = False
        self._light_hit_timer = 0
        
    def update(self, player, level, flashlight_on):
        """Обновление состояния врага"""
        # Проверка, находится ли враг в свете фонарика
        in_light = self.is_in_light(player, level)
        
        # Обработка эффекта света на врага
        if in_light and flashlight_on and self.visible:
            self.on_light_hit()
        else:
            # Сбрасываем флаг воспроизведения звука, если враг не в свете
            self._light_hit_played = False
        
        # Обновляем таймер звука
        if getattr(self, '_light_hit_timer', 0) > 0:
            self._light_hit_timer -= 1
            if self._light_hit_timer <= 0:
                self._light_hit_played = False
        
        # Обработка состояний
        self.handle_state(player, level, flashlight_on)
            
    @abstractmethod
    def on_light_hit(self):
        """Базовая реакция на попадание света (воспроизведение звука)"""
        if self.sound_manager and not getattr(self, '_light_hit_played', False):
            self.sound_manager.play_sound("light_hit_enemy")
            # Устанавливаем флаг, чтобы звук не воспроизводился непрерывно
            self._light_hit_played = True
            # Сбрасываем флаг через небольшое время
            self._light_hit_timer = 30  # Полсекунды при 60 FPS
        
    def handle_state(self, player, level, flashlight_on):
        """Обработка текущего состояния врага"""
        if self.state == "affected_by_light":
            self.effect_timer -= 1
            if self.effect_timer <= 0:
                self.state = "idle"
        elif self.state == "fading":
            self.effect_timer -= 1
            if self.effect_timer <= 0:
                self.visible = False
        elif not self.visible:
            return
        else:
            # Определение состояния врага (преследование или бездействие)
            distance = math.sqrt((player.rect.centerx - self.rect.centerx)**2 + 
                                (player.rect.centery - self.rect.centery)**2)
            
            if distance < ENEMY_DETECTION_RADIUS and self.visible:
                # Если до этого не преследовал игрока, издаем звук обнаружения
                if self.state != "chase" and self.sound_manager and not self.detected_player:
                    self.sound_manager.play_sound("enemy_detect")
                    self.detected_player = True
                
                self.state = "chase"
            elif self.state == "chase" and distance > ENEMY_CHASE_LIMIT:
                self.state = "idle"
                self.detected_player = False
                
            # Движение в зависимости от состояния
            if self.state == "chase" and self.visible:
                self.chase_player(player, level)
            elif self.state == "idle" and self.visible:
                self.idle_movement(level)
    
    def chase_player(self, player, level):
        """Преследование игрока"""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
        
        # Проверяем движение по осям отдельно для предотвращения "застревания"
        new_rect_x = self.rect.copy()
        new_rect_x.x += dx
        
        new_rect_y = self.rect.copy()
        new_rect_y.y += dy
        
        if not self.check_collision(new_rect_x, level):
            self.rect.x = new_rect_x.x
            
        if not self.check_collision(new_rect_y, level):
            self.rect.y = new_rect_y.y
    
    def idle_movement(self, level):
        """Случайное движение в режиме бездействия"""
        self.idle_timer += 1
        if self.idle_timer >= self.idle_duration:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.idle_timer = 0
            self.idle_duration = random.randint(60, 120)
        
        dx, dy = self.direction
        
        # Проверяем движение по осям отдельно
        new_rect_x = self.rect.copy()
        new_rect_x.x += dx * self.speed / 2
        
        new_rect_y = self.rect.copy()
        new_rect_y.y += dy * self.speed / 2
        
        if not self.check_collision(new_rect_x, level):
            self.rect.x = new_rect_x.x
        else:
            self.direction = (-dx, dy)  # Меняем направление по X
            
        if not self.check_collision(new_rect_y, level):
            self.rect.y = new_rect_y.y
        else:
            self.direction = (dx, -dy)  # Меняем направление по Y
    
    def check_collision(self, rect, level):
        """Проверка столкновений со стенами"""
        for wall in level.walls:
            if rect.colliderect(wall):
                return True
        return False
    
    def is_in_light(self, player, level):
        """Проверка, находится ли враг в конусе света фонарика"""
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > player.flashlight.get_current_radius():
            return False
        
        # Угол между игроком и врагом
        angle = math.atan2(dy, dx)
        angle_diff = abs(angle - player.flashlight.angle)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        if angle_diff > math.radians(LIGHT_ANGLE / 2):
            return False
            
        # Проверка, нет ли препятствий между игроком и врагом
        return self.has_line_of_sight(player.rect.centerx, player.rect.centery, 
                                     self.rect.centerx, self.rect.centery, level.walls)
    
    def has_line_of_sight(self, x1, y1, x2, y2, walls):
        """Проверяет, есть ли прямая видимость между двумя точками"""
        # Алгоритм Брезенхема для проверки линии
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        check_rect = pygame.Rect(0, 0, 4, 4)
        
        while x1 != x2 or y1 != y2:
            check_rect.x = x1 - 2
            check_rect.y = y1 - 2
            
            for wall in walls:
                if wall.colliderect(check_rect):
                    return False
                    
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
                
        return True
    
    def draw(self, screen, camera):
        """Отрисовка врага с учетом камеры"""
        if not self.visible:
            return
            
        enemy_rect = camera.apply(self.rect)
        
        # Проверяем, находится ли враг в пределах экрана
        if (enemy_rect.right >= 0 and enemy_rect.left <= SCREEN_WIDTH and 
            enemy_rect.bottom >= 0 and enemy_rect.top <= SCREEN_HEIGHT):
            
            if self.sprite:
                # Применяем смещение для центрирования спрайта
                sprite_rect = pygame.Rect(
                    enemy_rect.x - self.sprite_offset_x,
                    enemy_rect.y - self.sprite_offset_y,
                    enemy_rect.width + self.sprite_offset_x * 2,
                    enemy_rect.height + self.sprite_offset_y * 2
                )
                
                # Рисуем спрайт с учетом прозрачности
                if len(self.color) == 4:
                    # Создаем копию спрайта с нужной прозрачностью
                    alpha_sprite = self.sprite.copy()
                    alpha_sprite.set_alpha(self.color[3])
                    screen.blit(alpha_sprite, sprite_rect)
                else:
                    screen.blit(self.sprite, sprite_rect)
            else:
                # Запасной вариант с цветным прямоугольником
                # Если у врага есть прозрачность (4 компонента в цвете)
                if len(self.color) == 4:
                    # Создаем поверхность с прозрачностью
                    s = pygame.Surface((enemy_rect.width, enemy_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(s, self.color, (0, 0, enemy_rect.width, enemy_rect.height))
                    screen.blit(s, (enemy_rect.x, enemy_rect.y))
                else:
                    # Обычная отрисовка для непрозрачных врагов
                    pygame.draw.rect(screen, self.color, enemy_rect)


class ShadowEnemy(Enemy):
    """Теневой враг - исчезает при попадании света"""
    
    def __init__(self, x, y, sound_manager=None):
        super().__init__(x, y, ENEMY_SIZE, SHADOW_ENEMY_SPEED, SHADOW_ENEMY_COLOR, 
                         "assets/sprites/enemy/tile_0121.png", sound_manager)
    
    def on_light_hit(self):
        """При попадании света начинает исчезать"""
        # Воспроизводим базовый звук попадания света
        super().on_light_hit()
        
        if self.state != "fading":
            self.state = "fading"
            self.effect_timer = SHADOW_ENEMY_FADE_TIME


class GhostEnemy(Enemy):
    """Призрачный враг - замедляется при попадании света"""
    
    def __init__(self, x, y, sound_manager=None):
        super().__init__(x, y, ENEMY_SIZE, GHOST_ENEMY_SPEED, 
                        (GHOST_ENEMY_COLOR[0], GHOST_ENEMY_COLOR[1], 
                         GHOST_ENEMY_COLOR[2], GHOST_ENEMY_COLOR[3]), 
                         "assets/sprites/enemy/tile_0108.png", sound_manager)
        self.normal_speed = GHOST_ENEMY_SPEED
        self.light_speed = GHOST_ENEMY_LIGHT_SPEED
    
    def on_light_hit(self):
        """При попадании света замедляется"""
        # Воспроизводим базовый звук попадания света
        super().on_light_hit()
        
        self.state = "affected_by_light"
        self.effect_timer = GHOST_ENEMY_STUN_TIME
        self.speed = self.light_speed
        self.color = (GHOST_ENEMY_STUNNED_COLOR[0], GHOST_ENEMY_STUNNED_COLOR[1],
                      GHOST_ENEMY_STUNNED_COLOR[2], GHOST_ENEMY_STUNNED_COLOR[3])
  
    def handle_state(self, player, level, flashlight_on):
        """Обработка состояний с восстановлением скорости"""
        super().handle_state(player, level, flashlight_on)
        
        # Восстанавливаем нормальную скорость, если эффект света закончился
        if self.state != "affected_by_light" and self.speed != self.normal_speed:
            self.speed = self.normal_speed
            self.color = (GHOST_ENEMY_COLOR[0], GHOST_ENEMY_COLOR[1],
                          GHOST_ENEMY_COLOR[2], GHOST_ENEMY_COLOR[3])