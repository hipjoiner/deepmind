import random


class Player:
    def __init__(self, player_id, name, auto=False):
        self.id = player_id
        self.name = name
        self.auto = auto

    def __repr__(self):
        return 'Player %s' % self.name

    def actions(self, s):
        return s.actions(self.id)

    def action(self, s):
        if self.auto:
            i = random.randrange(len(self.actions(s)))
            return self.actions(s)[i]
        spot = input('Player %s: %s; move? ' % (self.name, self.actions(s)))
        return int(spot)
