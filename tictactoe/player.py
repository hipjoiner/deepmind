import random


class Player:
    def __init__(self, index, name, auto=False):
        self.index = index
        self.name = name
        self.auto = auto

    def __repr__(self):
        return 'Player %s' % self.name

    def action(self, s):
        """Choose and return action a"""
        p = self.policy(s)
        if not p:
            return None
        if not self.auto:
            spot = input('Player %s: %s; move? ' % (self.name, p))
            return int(spot)
        rnd = random.uniform(0, 1)
        cdf = 0
        for i, prob in enumerate(p):
            cdf += prob
            if rnd <= cdf:
                return s.actions[i]
        return s.actions[-1]

    def policy(self, s):
        """Return a list of probabilities (pdf) over all actions in s.actions"""
        if not s.actions:
            return []
        # Starting policy (no pre-existing): uniform random probability across action space
        return [1 / len(s.actions)] * len(s.actions)

        # How do we iteratively improve this policy?
