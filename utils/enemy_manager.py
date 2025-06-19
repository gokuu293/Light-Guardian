import pygame
import random
import math
from settings import *
from entities.enemy import ShadowEnemy, GhostEnemy

class EnemyManager:
    """Класс для управления врагами: создание, удаление, обновление с учетом комнатной структуры уровня"""
    
    def __init__(self):
        self.enemies = []
        self.shadow_spawn_timer = 0
        self.ghost_spawn_timer = 0
        self.max_shadows = 6  # Увеличиваем максимальное количество теневых врагов
        self.max_ghosts = 3
        self.shadow_spawn_interval = 600  # 10 секунд
        self.ghost_spawn_interval = 900   # 15 секунд
        self.initial_spawn_done = False   # Флаг для отслеживания начального спавна
        
        # Настройки спавна относительно игрока
        self.min_spawn_distance = 300     # Минимальное расстояние от игрока
        self.max_spawn_distance = 800     # Максимальное расстояние от игрока
        
        # Точки спавна определены в генерации уровня
        self.spawn_points = []
        
        # Комнатный контекст - отслеживаем, в какой комнате находится игрок
        self.current_room = None
        self.near_rooms = []  # Комнаты, соединенные с текущей
    
    def update(self, player, level):
        """Обновление всех врагов и управление спавном"""
        # Обновляем информацию о текущей комнате и соседних комнатах
        self._update_room_context(player, level)
        
        # Начальный спавн врагов при первом обновлении
        if not self.initial_spawn_done:
            self._initial_spawn(player, level)
            self.initial_spawn_done = True
        
        # Обновляем существующих врагов
        for enemy in self.enemies:
            enemy.update(player, level, player.flashlight.on)
        
        # Проверяем столкновения с игроком
        for enemy in self.enemies:
            if enemy.visible and player.rect.colliderect(enemy.rect):
                return "game_over"
        
        # Удаляем невидимых теневых врагов из списка
        self.enemies = [enemy for enemy in self.enemies if not (isinstance(enemy, ShadowEnemy) and not enemy.visible)]
        
        # Управляем спавном новых врагов
        self._manage_spawning(player, level)
        
        return None
    
    def _update_room_context(self, player, level):
        """Обновляет информацию о том, в какой комнате находится игрок и какие комнаты соседние"""
        # Проверяем, в какой комнате находится игрок
        player_room = None
        for room in level.rooms:
            if room.rect.collidepoint(player.rect.centerx, player.rect.centery):
                player_room = room
                break
        
        # Если игрок в комнате, находим соседние комнаты (те, которые соединены коридорами)
        if player_room:
            self.current_room = player_room
            self.near_rooms = []
            
            # Проверяем каждую дверь текущей комнаты
            for door in player_room.doors:
                # Ищем комнату, к которой ведет эта дверь
                for room in level.rooms:
                    if room == player_room:
                        continue
                    
                    # Проверяем, соединена ли эта комната с текущей комнатой
                    for corridor in level.corridors:
                        if corridor.colliderect(door["rect"]):
                            # Проверяем, соединяет ли этот коридор с другой комнатой
                            for other_door in room.doors:
                                if corridor.colliderect(other_door["rect"]):
                                    self.near_rooms.append(room)
                                    break
        else:
            # Если игрок не в комнате, проверяем коридоры
            for corridor in level.corridors:
                if corridor.collidepoint(player.rect.centerx, player.rect.centery):
                    # Находим комнаты, соединенные этим коридором
                    for room in level.rooms:
                        for door in room.doors:
                            if corridor.colliderect(door["rect"]):
                                self.near_rooms.append(room)
            
            # Если игрок не в комнате, текущая комната отсутствует
            self.current_room = None
    
    def _initial_spawn(self, player, level):
        """Создает начальных врагов при старте уровня в соответствующих комнатах"""
        # Не создаем врагов в стартовой комнате
        start_room = next((room for room in level.rooms if room.type == "start"), None)
        
        # Определяем сложные комнаты и обычные комнаты
        difficult_rooms = [room for room in level.rooms if room.type == "difficult" and room != start_room]
        normal_rooms = [room for room in level.rooms if room.type == "normal" and room != start_room]
        
        # Создаем врагов в сложных комнатах
        for room in difficult_rooms:
            if room.enemy_spawn_points:
                # Создаем 2-3 теневых врага в каждой сложной комнате (было 1-2)
                shadow_count = min(3, len(room.enemy_spawn_points))
                for i in range(shadow_count):
                    if i < len(room.enemy_spawn_points):
                        x, y = room.enemy_spawn_points[i]
                        self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                
                # Создаем 1-2 призрачных врагов, если осталось место для спавна (было 0-1)
                if shadow_count < len(room.enemy_spawn_points):
                    ghost_count = min(2, len(room.enemy_spawn_points) - shadow_count)
                    for i in range(ghost_count):
                        x, y = room.enemy_spawn_points[shadow_count + i]
                        self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
        
        # Создаем врагов в обычных комнатах
        for room in normal_rooms:
            if room.enemy_spawn_points:
                # В обычных комнатах 1-2 врагов (было 0-1)
                spawn_count = min(2, len(room.enemy_spawn_points))
                for i in range(spawn_count):
                    x, y = room.enemy_spawn_points[i]
                    # Чередуем типы врагов
                    if i % 2 == 0:
                        self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                    else:
                        self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
        
        # Если всё еще недостаточно врагов, используем старый метод спавна
        min_enemy_count = 6  # Увеличено с 3 до 6
        if len(self.enemies) < min_enemy_count:
            remaining = min_enemy_count - len(self.enemies)
            for i in range(remaining):
                if i % 2 == 0:
                    self._spawn_enemy_at_distance("shadow", player, level)
                else:
                    self._spawn_enemy_at_distance("ghost", player, level)
    
    def _manage_spawning(self, player, level):
        """Управление спавном врагов с учетом структуры комнат"""
        # Подсчет текущего количества врагов каждого типа
        shadow_count = sum(1 for enemy in self.enemies if isinstance(enemy, ShadowEnemy))
        ghost_count = sum(1 for enemy in self.enemies if isinstance(enemy, GhostEnemy))
        
        # Спавн теневых врагов
        if shadow_count < self.max_shadows:
            self.shadow_spawn_timer += 1
            if self.shadow_spawn_timer >= self.shadow_spawn_interval:
                self._spawn_enemy_smart("shadow", player, level)
                self.shadow_spawn_timer = 0
        
        # Спавн призрачных врагов
        if ghost_count < self.max_ghosts:
            self.ghost_spawn_timer += 1
            if self.ghost_spawn_timer >= self.ghost_spawn_interval:
                self._spawn_enemy_smart("ghost", player, level)
                self.ghost_spawn_timer = 0
    
    def _spawn_enemy_smart(self, enemy_type, player, level):
        """Интеллектуальный спавн врагов с учетом текущей комнаты игрока"""
        # Стратегия 1: Спавн в соседних комнатах (но не в текущей)
        if self.near_rooms:
            # Выбираем случайную соседнюю комнату
            spawn_room = random.choice(self.near_rooms)
            
            # Проверяем, есть ли в ней точки спавна
            if spawn_room.enemy_spawn_points:
                x, y = random.choice(spawn_room.enemy_spawn_points)
                
                # Проверяем, не слишком ли близко к игроку
                distance = math.sqrt((player.rect.centerx - x)**2 + (player.rect.centery - y)**2)
                if distance >= self.min_spawn_distance:
                    if enemy_type == "shadow":
                        self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                    elif enemy_type == "ghost":
                        self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                    return True
        
        # Стратегия 2: Используем предопределенные точки спавна
        if self.spawn_points:
            # Отфильтровываем точки, которые не в текущей комнате игрока и не слишком близко
            valid_points = []
            for x, y in self.spawn_points:
                # Проверяем расстояние до игрока
                distance = math.sqrt((player.rect.centerx - x)**2 + (player.rect.centery - y)**2)
                
                # Проверяем, не в текущей ли комнате игрока эта точка
                in_current_room = False
                if self.current_room:
                    in_current_room = self.current_room.rect.collidepoint(x, y)
                
                if distance >= self.min_spawn_distance and not in_current_room:
                    valid_points.append((x, y))
            
            if valid_points:
                x, y = random.choice(valid_points)
                if enemy_type == "shadow":
                    self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                elif enemy_type == "ghost":
                    self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                return True
        
        # Стратегия 3: Запасной вариант - спавн на расстоянии от игрока
        return self._spawn_enemy_at_distance(enemy_type, player, level)
    
    def _spawn_enemy_at_distance(self, enemy_type, player, level):
        """Создает врага на определенном расстоянии от игрока (запасной метод)"""
        max_attempts = 50  # Максимальное количество попыток найти подходящее место
        
        for _ in range(max_attempts):
            # Генерируем случайный угол
            angle = random.uniform(0, 2 * math.pi)
            
            # Генерируем случайное расстояние в заданном диапазоне
            distance = random.uniform(self.min_spawn_distance, self.max_spawn_distance)
            
            # Вычисляем координаты
            x = player.rect.centerx + math.cos(angle) * distance
            y = player.rect.centery + math.sin(angle) * distance
            
            # Проверяем, не выходит ли за границы карты
            if x < 50 or x > MAP_WIDTH - 50 or y < 50 or y > MAP_HEIGHT - 50:
                continue
            
            # Проверяем, не в стартовой ли или финальной комнате
            in_special_room = False
            for room in level.rooms:
                if (room.type == "start" or room.type == "exit") and room.rect.collidepoint(x, y):
                    in_special_room = True
                    break
            
            if in_special_room:
                continue
            
            # Создаем временный прямоугольник с увеличенным запасом для проверки коллизий
            safety_margin = 10  # Добавляем запас безопасности
            test_rect = pygame.Rect(
                x - ENEMY_SIZE/2 - safety_margin, 
                y - ENEMY_SIZE/2 - safety_margin, 
                ENEMY_SIZE + safety_margin*2, 
                ENEMY_SIZE + safety_margin*2
            )
            
            # Проверяем коллизии со стенами
            wall_collision = False
            for wall in level.walls:
                if test_rect.colliderect(wall):
                    wall_collision = True
                    break
            
            if not wall_collision:
                # Создаем врага нужного типа
                if enemy_type == "shadow":
                    self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                elif enemy_type == "ghost":
                    self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                return True
        
        # Если не удалось найти подходящее место, используем самый запасной метод
        return self._fallback_spawn(enemy_type, level)
    
    def _fallback_spawn(self, enemy_type, level):
        """Запасной метод спавна, ищет любое подходящее место на карте"""
        # Пытаемся найти случайную обычную или сложную комнату
        eligible_rooms = [r for r in level.rooms if r.type in ["normal", "difficult"]]
        
        if eligible_rooms:
            # Выбираем случайную подходящую комнату
            room = random.choice(eligible_rooms)
            
            # Увеличиваем отступ от стен для большей безопасности
            padding = WALL_THICKNESS + 70  # Увеличено с 50
            for _ in range(30):  # Увеличиваем количество попыток с 20 до 30
                x = random.randint(room.rect.x + padding, room.rect.x + room.rect.width - padding)
                y = random.randint(room.rect.y + padding, room.rect.y + room.rect.height - padding)
                
                # Создаем временный прямоугольник с увеличенным запасом для проверки коллизий
                safety_margin = 15  # Добавляем запас безопасности
                test_rect = pygame.Rect(
                    x - ENEMY_SIZE/2 - safety_margin, 
                    y - ENEMY_SIZE/2 - safety_margin, 
                    ENEMY_SIZE + safety_margin*2, 
                    ENEMY_SIZE + safety_margin*2
                )
                
                # Проверяем коллизии со ВСЕМИ стенами и препятствиями
                wall_collision = False
                for wall in level.walls:
                    if test_rect.colliderect(wall):
                        wall_collision = True
                        break
                
                if not wall_collision:
                    # Создаем врага нужного типа
                    if enemy_type == "shadow":
                        self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                    elif enemy_type == "ghost":
                        self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                    return True
        
        # Если всё-таки не получилось, пробуем старый метод случайного размещения
        # с дополнительными проверками
        for _ in range(30):  # Увеличим количество попыток
            x = random.randint(150, MAP_WIDTH - 150)  # Увеличиваем отступ от краев
            y = random.randint(150, MAP_HEIGHT - 150)
            
            # Проверяем, не в стартовой ли или финальной комнате
            in_special_room = False
            for room in level.rooms:
                if (room.type == "start" or room.type == "exit") and room.rect.collidepoint(x, y):
                    in_special_room = True
                    break
            
            if in_special_room:
                continue
            
            # Увеличенный запас для проверки коллизий
            safety_margin = 15
            test_rect = pygame.Rect(
                x - ENEMY_SIZE/2 - safety_margin, 
                y - ENEMY_SIZE/2 - safety_margin, 
                ENEMY_SIZE + safety_margin*2, 
                ENEMY_SIZE + safety_margin*2
            )
            
            # Проверка ВСЕХ возможных коллизий
            wall_collision = False
            for wall in level.walls:
                if test_rect.colliderect(wall):
                    wall_collision = True
                    break
            
            if not wall_collision:
                # Создаем врага нужного типа
                if enemy_type == "shadow":
                    self.enemies.append(ShadowEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                elif enemy_type == "ghost":
                    self.enemies.append(GhostEnemy(x - ENEMY_SIZE/2, y - ENEMY_SIZE/2))
                return True
        
        # Если все попытки не удались, просто возвращаем False
        return False
    
    def draw(self, screen, camera):
        """Отрисовка всех врагов"""
        for enemy in self.enemies:
            enemy.draw(screen, camera)
    
    def reset(self):
        """Сброс всех врагов"""
        self.enemies.clear()
        self.shadow_spawn_timer = 0
        self.ghost_spawn_timer = 0
        self.initial_spawn_done = False
        self.current_room = None
        self.near_rooms = []