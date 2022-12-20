from config import CachedInstance


class Player(metaclass=CachedInstance):
    def __init__(self, symbol, number=None, auto=True):
        self.symbol = symbol
        self.number = number
        self.auto = auto
