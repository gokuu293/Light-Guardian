class Player:
    def __init__(self):
        self.x = 400      # Начальная позиция X
        self.y = 300      # Начальная позиция Y
        self.speed = 5    # Скорость перемещения
        self.radius = 10  # Размер игрока (для коллизий)