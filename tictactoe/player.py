import random


class Player:
    def __init__(self, player_id, name, auto=False):
        self.id = player_id
        self.name = name
        self.auto = auto

    def __repr__(self):
        return 'Player %d (%s)' % (self.id, self.name)

    def policy(self, s):
        if not self.auto:
            spot = input('Player %s: %s; move? ' % (self.name, s.actions))
            return int(spot)
        # Simplest policy: choose at random from available actions
        i = random.randrange(len(s.actions))
        return s.actions[i]
