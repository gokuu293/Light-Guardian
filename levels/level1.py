import pygame
import random
import math
from settings import *
from utils.enemy_manager import EnemyManager
from levels.room import Room


class Level1:
    def __init__(self, sound_manager=None):
        # Сохраняем звуковой менеджер
        self.sound_manager = sound_manager
        
        # Создаем большую карту подземелья
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        
        # Комнаты и коридоры
        self.rooms = []
        self.corridors = []
        
        # Все стены (включая стены комнат и коридоров)
        self.walls = []
        
        # Заполняем всю карту стенами (сплошным камнем)
        self._fill_map_with_walls()
        
        # Генерируем структуру уровня - вырезаем комнаты из сплошного камня
        self._generate_rooms()
        self._connect_rooms()
        
        # Проверяем, что все комнаты связаны и исправляем при необходимости
        self._ensure_path_exists()
        
        # Собираем все стены из комнат и коридоров
        self._collect_walls()
        
        # Батарейки для пополнения заряда
        self.batteries = []
        self._collect_batteries()
        
        # Менеджер врагов
        self.enemy_manager = EnemyManager(self, sound_manager)
        self._setup_enemies()
        
        # Позиция старта игрока (центр стартовой комнаты)
        self.start_position = self._get_start_position()
        
        # Выход с уровня (центр финальной комнаты)
        self.exit = self._create_exit()
    
        # Загрузка спрайтов для игровых объектов
        self.battery_sprite = None
        self.exit_sprites = []  # Список для кадров анимации портала
        self.exit_frame = 0     # Текущий кадр анимации
        self.exit_animation_timer = 0  # Таймер для управления скоростью анимации
        self._load_sprites()
    
    def _fill_map_with_walls(self):
        """Заполняет всю карту стенами (сплошным камнем)"""
        # Размер блока стены
        block_size = 50
        
        # Создаем сетку стен, заполняющую всю карту
        self.solid_walls = []
        for x in range(0, self.width, block_size):
            for y in range(0, self.height, block_size):
                # Внешний край карты делаем толще
                if (x < WALL_THICKNESS or x > self.width - WALL_THICKNESS - block_size or 
                    y < WALL_THICKNESS or y > self.height - WALL_THICKNESS - block_size):
                    self.solid_walls.append(pygame.Rect(x, y, block_size, block_size))
                else:
                    # Внутренние стены с вероятностью 90% (было 95%)
                    # Это создаст немного более просторные "естественные пещеры" среди стен
                    if random.random() < 0.90:
                        self.solid_walls.append(pygame.Rect(x, y, block_size, block_size))
    
    def _generate_rooms(self):
        """Генерирует комнаты разных типов с увеличенным размером"""
        # Сетка для размещения комнат
        grid_cols = 3
        grid_rows = 3
        cell_width = self.width // grid_cols
        cell_height = self.height // grid_rows
        
        # Типы комнат для различных позиций
        room_types = {
            (0, 0): "start",  # Левый верхний угол - стартовая комната
            (grid_cols-1, grid_rows-1): "exit"  # Правый нижний угол - комната с выходом
        }
        
        # Комнаты, которые обязательно должны быть включены
        must_have_cells = [(0, 0), (grid_cols-1, grid_rows-1)]
        
        # Для каждой ячейки создаем одну комнату
        for i in range(grid_cols):
            for j in range(grid_rows):
                # Пропускаем некоторые комнаты для разнообразия, если они не обязательные
                if (i, j) not in must_have_cells and random.random() < 0.2:
                    continue
                    
                # Определяем тип комнаты
                room_type = room_types.get((i, j), "normal")
                
                # С вероятностью 25% обычная комната может стать сложной
                if room_type == "normal" and random.random() < 0.25:
                    room_type = "difficult"
                
                if room_type == "start":
                    width = int(cell_width * 0.75)  
                    height = int(cell_height * 0.75)  
                elif room_type == "exit":
                    width = int(cell_width * 0.70)  
                    height = int(cell_height * 0.70)  
                else:
                    width = int(cell_width * random.uniform(0.60, 0.80))  
                    height = int(cell_height * random.uniform(0.60, 0.80))  
                
                # Координаты комнаты (с отступом от краев ячейки для коридоров)
                padding_x = (cell_width - width) // 2
                padding_y = (cell_height - height) // 2
                x = i * cell_width + padding_x
                y = j * cell_height + padding_y
                
                # Создаем комнату
                room = Room(x, y, width, height, room_type)
                self.rooms.append(room)
                
                # Добавляем батарейки в комнату
                if room_type == "start":
                    room.add_battery(1)  # Одна батарейка в стартовой комнате
                elif room_type == "difficult":
                    room.add_battery(2)  # Две батарейки в сложной комнате
                elif room_type == "normal":
                    room.add_battery(1 if random.random() < 0.7 else 0)  # 70% шанс батарейки
        
        # Вырезаем комнаты из сплошных стен
        self._carve_rooms_from_walls()
    
    def _carve_rooms_from_walls(self):
        """Вырезает комнаты из сплошного камня"""
        # Для каждой комнаты убираем все стены, которые находятся внутри неё
        for room in self.rooms:
            # Создаем немного увеличенный прямоугольник комнаты для надежности
            carve_rect = pygame.Rect(
                room.rect.x - 5, 
                room.rect.y - 5, 
                room.rect.width + 10, 
                room.rect.height + 10
            )
            
            # Удаляем стены внутри комнаты
            self.solid_walls = [wall for wall in self.solid_walls 
                              if not carve_rect.contains(wall)]
    
    def _connect_rooms(self):
        """Соединяет комнаты коридорами, вырезая проходы в сплошном камне"""
        if not self.rooms:
            return
            
        # Создаем граф соединений между комнатами (минимальное остовное дерево)
        connected = set()
        start_room = next((room for room in self.rooms if room.type == "start"), self.rooms[0])
        connected.add(start_room)
        
        # Пока не все комнаты соединены
        while len(connected) < len(self.rooms):
            best_connection = None
            shortest_distance = float('inf')
            
            # Ищем ближайшую несоединенную комнату к любой соединенной
            for room1 in connected:
                for room2 in self.rooms:
                    if room2 in connected:
                        continue
                    
                    # Считаем расстояние между центрами комнат
                    distance = ((room1.rect.centerx - room2.rect.centerx) ** 2 + 
                                (room1.rect.centery - room2.rect.centery) ** 2) ** 0.5
                    
                    if distance < shortest_distance:
                        shortest_distance = distance
                        best_connection = (room1, room2)
            
            if best_connection:
                # Создаем коридор и вырезаем его из сплошных стен
                self._create_corridor(*best_connection)
                connected.add(best_connection[1])
        
        # Добавляем несколько дополнительных коридоров для циклов (чтобы было несколько путей)
        for _ in range(2):  # Добавляем 2 случайных дополнительных коридора
            # Выбираем две случайные комнаты
            if len(self.rooms) >= 2:
                room1, room2 = random.sample(self.rooms, 2)
                # Если это не одна и та же комната и они не соединены напрямую
                if room1 != room2:
                    self._create_corridor(room1, room2)
    
    def _create_corridor(self, room1, room2):
        """Создает коридор между двумя комнатами, вырезая проход в сплошном камне"""
        # Определяем начальную и конечную точки коридора (центры комнат)
        start_x, start_y = room1.rect.center
        end_x, end_y = room2.rect.center
        
        # Добавляем коридор в список
        corridor_rect = self._create_corridor_rect(start_x, start_y, end_x, end_y)
        self.corridors.append(corridor_rect)
        
        # Вырезаем коридор из сплошных стен
        self._carve_corridor_from_walls(corridor_rect)
        
        # Добавляем двери в комнаты (для визуального эффекта)
        if abs(start_x - end_x) > abs(start_y - end_y):
            # Горизонтальный коридор
            if start_x < end_x:
                room1.add_door("right")
                room2.add_door("left")
            else:
                room1.add_door("left")
                room2.add_door("right")
        else:
            # Вертикальный коридор
            if start_y < end_y:
                room1.add_door("bottom")
                room2.add_door("top")
            else:
                room1.add_door("top")
                room2.add_door("bottom")
                
        return True
    
    def _create_corridor_rect(self, start_x, start_y, end_x, end_y):
        """Создает прямоугольник коридора с поворотом под прямым углом"""
        corridor_width = 80  
        
        # Определяем, будет ли поворот сначала по горизонтали, затем по вертикали,
        # или наоборот (случайно, для разнообразия)
        if random.random() < 0.5:
            # Сначала горизонтальный участок, затем вертикальный
            bend_x = end_x
            bend_y = start_y
        else:
            # Сначала вертикальный участок, затем горизонтальный
            bend_x = start_x
            bend_y = end_y
            
        # Создаем два участка коридора
        if abs(start_x - bend_x) > abs(start_y - bend_y):
            # Первый участок горизонтальный
            section1 = pygame.Rect(
                min(start_x, bend_x) - corridor_width//2,
                start_y - corridor_width//2,
                abs(start_x - bend_x) + corridor_width,
                corridor_width
            )
            # Второй участок вертикальный
            section2 = pygame.Rect(
                bend_x - corridor_width//2,
                min(bend_y, end_y) - corridor_width//2,
                corridor_width,
                abs(bend_y - end_y) + corridor_width
            )
        else:
            # Первый участок вертикальный
            section1 = pygame.Rect(
                start_x - corridor_width//2,
                min(start_y, bend_y) - corridor_width//2,
                corridor_width,
                abs(start_y - bend_y) + corridor_width
            )
            # Второй участок горизонтальный
            section2 = pygame.Rect(
                min(bend_x, end_x) - corridor_width//2,
                bend_y - corridor_width//2,
                abs(bend_x - end_x) + corridor_width,
                corridor_width
            )
            
        # Объединяем два участка в один прямоугольник
        combined_rect = section1.union(section2)
        return combined_rect
    
    def _carve_corridor_from_walls(self, corridor_rect):
        """Вырезает коридор из сплошных стен"""
        # Удаляем все стены, которые перекрываются с коридором
        self.solid_walls = [wall for wall in self.solid_walls
                           if not corridor_rect.contains(wall) and not wall.colliderect(corridor_rect)]
    
    def _collect_walls(self):
        """Собирает все стены для обработки коллизий"""
        # Сначала добавляем внешние стены карты
        self.walls = [
            # Верхняя граница
            pygame.Rect(0, 0, self.width, WALL_THICKNESS),
            # Левая граница
            pygame.Rect(0, 0, WALL_THICKNESS, self.height),
            # Нижняя граница
            pygame.Rect(0, self.height - WALL_THICKNESS, self.width, WALL_THICKNESS),
            # Правая граница
            pygame.Rect(self.width - WALL_THICKNESS, 0, WALL_THICKNESS, self.height)
        ]
        
        # Добавляем все оставшиеся сплошные стены
        self.walls.extend(self.solid_walls)
        
        # Добавляем препятствия внутри комнат
        for room in self.rooms:
            for obstacle in room.obstacles:
                self.walls.append(obstacle)
    
    def _collect_batteries(self):
        """Собирает все батарейки из комнат"""
        self.batteries = []  # Сначала очищаем список
        for room in self.rooms:
            self.batteries.extend(room.batteries)
    
    def _setup_enemies(self):
        """Настраивает спавн врагов в комнатах с проверкой валидности точек спавна"""
        # Очищаем список точек спавна
        spawn_points = []
        
        for room in self.rooms:
            # Не размещаем врагов в стартовой и финальной комнатах
            if room.type == "start" or room.type == "exit":
                continue
            
            # Фильтруем точки спавна, удаляя те, что находятся в стенах
            valid_spawn_points = []
            for x, y in room.enemy_spawn_points:
                # Создаем увеличенный прямоугольник для более надежной проверки
                enemy_rect = pygame.Rect(
                    x - ENEMY_SIZE/2 - 5,  # Дополнительное пространство для безопасности
                    y - ENEMY_SIZE/2 - 5, 
                    ENEMY_SIZE + 10, 
                    ENEMY_SIZE + 10
                )
                
                # Проверяем коллизии со ВСЕМИ стенами уровня
                if not any(enemy_rect.colliderect(wall) for wall in self.walls):
                    # Также проверяем, не находится ли точка спавна внутри припятствий других комнат
                    in_other_room_obstacle = False
                    for other_room in self.rooms:
                        if other_room != room:
                            for obstacle in other_room.obstacles:
                                if enemy_rect.colliderect(obstacle):
                                    in_other_room_obstacle = True
                                    break
                            if in_other_room_obstacle:
                                break
                    
                    if not in_other_room_obstacle:
                        valid_spawn_points.append((x, y))
            
            # Устанавливаем интервалы очков спавна внутри комнат
            if valid_spawn_points:
                # В сложных комнатах больше врагов
                if room.type == "difficult":
                    spawn_count = min(3, len(valid_spawn_points))
                    if spawn_count > 0:
                        selected_points = random.sample(valid_spawn_points, spawn_count)
                        spawn_points.extend(selected_points)
                # В обычных комнатах врагов меньше
                elif room.type == "normal":
                    spawn_count = min(1, len(valid_spawn_points))
                    if spawn_count > 0:
                        selected_points = random.sample(valid_spawn_points, spawn_count)
                        spawn_points.extend(selected_points)
        
        # Передаем очищенный список точек спавна менеджеру врагов
        self.enemy_manager.spawn_points = spawn_points
    
    def _get_start_position(self):
        """Возвращает начальную позицию игрока (центр стартовой комнаты)"""
        start_room = next((room for room in self.rooms if room.type == "start"), None)
        if start_room:
            # Возвращаем центр комнаты, что гарантирует, что игрок не начнет в стене
            return start_room.get_center()
        return (100, 100)  # Запасная позиция
    
    def _create_exit(self):
        """Создает выход в комнате типа 'exit', гарантируя, что он не в стене"""
        exit_room = next((room for room in self.rooms if room.type == "exit"), None)
        if exit_room:
            # Создаем выход в центре комнаты, но с проверкой на коллизии
            center_x, center_y = exit_room.get_center()
            
            # Проверяем, что центр комнаты не перекрывается со стенами
            exit_rect = pygame.Rect(
                center_x - EXIT_SIZE // 2, 
                center_y - EXIT_SIZE // 2,
                EXIT_SIZE, EXIT_SIZE
            )
            
            # Если выход в стене, ищем безопасное место в комнате
            if any(exit_rect.colliderect(wall) for wall in self.walls):
                # Пробуем несколько позиций внутри комнаты
                for offset_x in range(-50, 51, 25):
                    for offset_y in range(-50, 51, 25):
                        test_x = center_x + offset_x
                        test_y = center_y + offset_y
                        
                        if exit_room.rect.collidepoint(test_x, test_y):
                            test_rect = pygame.Rect(
                                test_x - EXIT_SIZE // 2, 
                                test_y - EXIT_SIZE // 2,
                                EXIT_SIZE, EXIT_SIZE
                            )
                            
                            if not any(test_rect.colliderect(wall) for wall in self.walls):
                                return test_rect
                
                # Если не нашли безопасное место, создаем безопасную зону
                safe_area = pygame.Rect(
                    center_x - EXIT_SIZE, 
                    center_y - EXIT_SIZE,
                    EXIT_SIZE * 2, EXIT_SIZE * 2
                )
                
                # Удаляем все стены в области выхода
                self.walls = [wall for wall in self.walls if not safe_area.colliderect(wall)]
                
                # Возвращаем исходную позицию выхода, которая теперь безопасна
                return exit_rect
            
            return exit_rect
        
        # Запасной вариант
        return pygame.Rect(self.width-100, self.height-100, EXIT_SIZE, EXIT_SIZE)
    
    def add_battery(self, x=None, y=None):
        """Добавляет новую батарейку в указанной позиции или в случайной комнате"""
        if x is None or y is None:
            # Выбираем случайную комнату типа "normal" или "difficult"
            eligible_rooms = [r for r in self.rooms if r.type in ["normal", "difficult"]]
            if eligible_rooms:
                room = random.choice(eligible_rooms)
                room.add_battery(1)
                self._collect_batteries()  # Обновляем общий список батареек
                return True
            return False
        else:
            # Проверяем, находится ли позиция внутри какой-либо комнаты
            battery_rect = pygame.Rect(x, y, BATTERY_SIZE, BATTERY_SIZE)
            
            for room in self.rooms:
                if room.rect.contains(battery_rect):
                    # Проверяем коллизии со стенами и объектами
                    collision = False
                    for wall in self.walls:
                        if battery_rect.colliderect(wall):
                            collision = True
                            break
                    
                    if not collision:
                        for other_battery in self.batteries:
                            if battery_rect.colliderect(other_battery):
                                collision = True
                                break
                    
                    if not collision:
                        self.batteries.append(battery_rect)
                        return True
            
            return False

    def update(self, player):
        # Обновление врагов через менеджер
        enemy_result = self.enemy_manager.update(player, self)
        if enemy_result == "game_over":
            return "game_over"
        
        # Проверка сбора батареек
        for battery in self.batteries[:]:
            if player.rect.colliderect(battery):
                player.add_battery(BATTERY_CHARGE)
                self.batteries.remove(battery)
                
                # Шанс появления новой батарейки в другом месте (30%)
                if random.random() < 0.3:
                    self.add_battery()
        
        # Проверка достижения выхода
        if player.rect.colliderect(self.exit):
            # Проигрываем звук победы
            if hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_sound("level_complete")
            return "level_complete"
            
        # Обновление анимации портала
        self.exit_animation_timer += 1
        if self.exit_animation_timer >= 10:  # Меняем кадр каждые 10 обновлений (примерно 6 кадров в секунду при 60 FPS)
            self.exit_animation_timer = 0
            self.exit_frame = (self.exit_frame + 1) % len(self.exit_sprites)
        
        return None

    def draw(self, screen, camera):
        # Рисуем пол подземелья
        screen.fill(DUNGEON_FLOOR)
        
        # Стены - рисуем только те, что видны на экране
        for wall in self.walls:
            wall_rect = camera.apply(wall)
            # Проверяем, находится ли стена в пределах экрана
            if (wall_rect.right >= 0 and wall_rect.left <= SCREEN_WIDTH and 
                wall_rect.bottom >= 0 and wall_rect.top <= SCREEN_HEIGHT):
                pygame.draw.rect(screen, WALL_COLOR, wall_rect)
        
        # Батарейки - рисуем только видимые
        for battery in self.batteries:
            battery_rect = camera.apply(battery)
            if (battery_rect.right >= 0 and battery_rect.left <= SCREEN_WIDTH and 
                battery_rect.bottom >= 0 and battery_rect.top <= SCREEN_HEIGHT):
                if self.battery_sprite:
                    # Применяем смещение для центрирования
                    sprite_rect = pygame.Rect(
                        battery_rect.x - self.battery_offset,
                        battery_rect.y - self.battery_offset,
                        battery_rect.width + self.battery_offset * 2,
                        battery_rect.height + self.battery_offset * 2
                    )
                    screen.blit(self.battery_sprite, sprite_rect)
                else:
                    pygame.draw.rect(screen, (0, 255, 0), battery_rect)
        
        # Отрисовка врагов через менеджер
        self.enemy_manager.draw(screen, camera)
        
        # Выход с анимацией
        exit_rect = camera.apply(self.exit)
        if (exit_rect.right >= 0 and exit_rect.left <= SCREEN_WIDTH and 
            exit_rect.bottom >= 0 and exit_rect.top <= SCREEN_HEIGHT):
            if self.exit_sprites:
                # Выбираем текущий кадр анимации
                current_sprite = self.exit_sprites[self.exit_frame]
                
                # Применяем смещение для центрирования
                sprite_rect = pygame.Rect(
                    exit_rect.x - self.exit_offset,
                    exit_rect.y - self.exit_offset,
                    exit_rect.width + self.exit_offset * 2,
                    exit_rect.height + self.exit_offset * 2
                )
                
                screen.blit(current_sprite, sprite_rect)
            else:
                pygame.draw.rect(screen, (255, 0, 0), exit_rect)

    def _ensure_path_exists(self):
        """Проверяет, что между всеми комнатами есть проход, и добавляет коридоры при необходимости"""
        # Создаем граф соединений между комнатами
        connected_rooms = {}
        for room in self.rooms:
            connected_rooms[room] = []
        
        # Проверяем, какие комнаты соединены
        for corridor in self.corridors:
            rooms_connected = []
            for room in self.rooms:
                # Проверяем, соединяется ли коридор с комнатой
                if any(door["rect"].colliderect(corridor) for door in room.doors):
                    rooms_connected.append(room)
            
            # Если коридор соединяет две комнаты, добавляем их в граф
            if len(rooms_connected) >= 2:
                for i in range(len(rooms_connected)):
                    for j in range(i+1, len(rooms_connected)):
                        if rooms_connected[j] not in connected_rooms[rooms_connected[i]]:
                            connected_rooms[rooms_connected[i]].append(rooms_connected[j])
                        if rooms_connected[i] not in connected_rooms[rooms_connected[j]]:
                            connected_rooms[rooms_connected[j]].append(rooms_connected[i])
        
        # Проверяем достижимость всех комнат из стартовой комнаты
        start_room = next((room for room in self.rooms if room.type == "start"), None)
        if not start_room:
            return  # Если нет стартовой комнаты, ничего не делаем
        
        # Проверка с помощью BFS
        visited = {room: False for room in self.rooms}
        queue = [start_room]
        visited[start_room] = True
        
        while queue:
            current_room = queue.pop(0)
            for neighbor in connected_rooms[current_room]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        
        # Проверяем, есть ли недоступные комнаты
        for room, is_visited in visited.items():
            if not is_visited:
                # Комната недоступна, соединяем её с ближайшей доступной
                closest_room = None
                min_distance = float('inf')
                
                for connected_room in self.rooms:
                    if visited[connected_room]:
                        distance = ((room.rect.centerx - connected_room.rect.centerx) ** 2 +
                                    (room.rect.centery - connected_room.rect.centery) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_room = connected_room
                
                # Создаем коридор между недоступной комнатой и ближайшей доступной
                if closest_room:
                    success = self._create_corridor(room, closest_room)
                    # Если успешно создали коридор, отмечаем комнату как посещенную
                    if success:
                        visited[room] = True
                        # Добавляем связи в граф
                        if closest_room not in connected_rooms[room]:
                            connected_rooms[room].append(closest_room)
                        if room not in connected_rooms[closest_room]:
                            connected_rooms[closest_room].append(room)

    def _load_sprites(self):
        """Загружает спрайты для игровых объектов"""
        try:
            # Загружаем спрайт батарейки
            self.battery_sprite = pygame.image.load("assets/sprites/items/battery.png").convert_alpha()
            
            # Увеличиваем размер батарейки (в 1.5 раза)
            battery_size = int(BATTERY_SIZE * 1.5)
            self.battery_sprite = pygame.transform.scale(self.battery_sprite, (battery_size, battery_size))
            self.battery_offset = (battery_size - BATTERY_SIZE) // 2
            
            # Загружаем кадры анимации портала
            portal1 = pygame.image.load("assets/sprites/items/portalRings1.png").convert_alpha()
            portal2 = pygame.image.load("assets/sprites/items/portalRings2.png").convert_alpha()
            
            # Увеличиваем размер портала (в 2 раза)
            exit_size = EXIT_SIZE * 2
            portal1 = pygame.transform.scale(portal1, (exit_size, exit_size))
            portal2 = pygame.transform.scale(portal2, (exit_size, exit_size))
            
            self.exit_sprites = [portal1, portal2]
            self.exit_offset = (exit_size - EXIT_SIZE) // 2
            
        except Exception as e:
            print(f"Ошибка загрузки спрайтов: {e}")
            self.battery_sprite = None
            self.exit_sprites = []