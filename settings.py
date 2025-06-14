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
LIGHT_RADIUS = 200  # Увеличено со 150
LIGHT_ANGLE = 45
LIGHT_DRAIN = 0.1

# Размеры стен
WALL_THICKNESS = 20  # Толщина внешних стен

# Враги
ENEMY_SIZE = 25
ENEMY_SPEED = 2
ENEMY_COLOR = (150, 0, 0)
ENEMY_STUNNED_COLOR = (100, 100, 100)
ENEMY_DETECTION_RADIUS = 200
ENEMY_CHASE_LIMIT = 300
ENEMY_STUN_TIME = 180  # 3 секунды при 60 FPS

# Карта
MAP_WIDTH = 2560  # Увеличенный размер карты (в 2 раза шире экрана)
MAP_HEIGHT = 1440  # Увеличенный размер карты (в 2 раза выше экрана)