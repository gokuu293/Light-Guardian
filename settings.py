# Настройки экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = False  # Флаг для полноэкранного режима

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (30, 30, 30)
LIGHT_AMBER = (255, 191, 0, 180)  # RGBA для фонарика
DUNGEON_FLOOR = (50, 45, 40)  # Цвет пола подземелья

# Игрок
PLAYER_SPEED = 4
PLAYER_SIZE = 20

# Фонарик
LIGHT_RADIUS = 200
LIGHT_ANGLE = 45
LIGHT_DRAIN = 0.1

# Размеры стен
WALL_THICKNESS = 20  # Толщина внешних стен

# Общие настройки врагов
ENEMY_SIZE = 25
ENEMY_DETECTION_RADIUS = 250
ENEMY_CHASE_LIMIT = 350

# Теневой враг (исчезает на свету)
SHADOW_ENEMY_SPEED = 2.5
SHADOW_ENEMY_COLOR = (20, 20, 30)
SHADOW_ENEMY_FADE_TIME = 60  # 1 секунда при 60 FPS
SHADOW_ENEMY_SPAWN_TIME = 300  # 5 секунд при 60 FPS

# Призрачный враг (замедляется на свету)
GHOST_ENEMY_SPEED = 2
GHOST_ENEMY_COLOR = (80, 80, 150, 150)
GHOST_ENEMY_STUNNED_COLOR = (60, 60, 100, 100)
GHOST_ENEMY_LIGHT_SPEED = 0.5  # Скорость при свете
GHOST_ENEMY_STUN_TIME = 180  # 3 секунды при 60 FPS

# Карта
MAP_WIDTH = 2560  # Увеличенный размер карты (в 2 раза шире экрана)
MAP_HEIGHT = 1440  # Увеличенный размер карты (в 2 раза выше экрана)

# Игровые объекты
BATTERY_SIZE = 20
BATTERY_CHARGE = 25  # Процент заряда от одной батарейки
EXIT_SIZE = 40