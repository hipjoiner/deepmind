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
        if not self.auto:
            spot = input('Player %s: %s; move? ' % (self.name, s.actions))
            return int(spot)
        pass

    def action_value(self, s, a):
        return s.transitions[a].state_value

    def action_values(self, s):
        return [s.transitions[a].state_value for a in s.actions]

    def policy(self, s):
        """Return a dict keyed by action containing the probability of taking
        that action, for all actions in state s"""

        # Starting policy (no pre-existing): uniform random probability across action space
        if not s.actions:
            return []
        p = 1 / len(s.actions)
        return [p] * len(s.actions)

        """ 
        Next:  Find max of all states.  If a tie, choose at random.
        """
        max_val = -1
        maxes = []
        for a in s.actions:
            s_prime = s.transitions[a]
            val = s_prime.state_value[self.index]
            if val < max_val:
                continue
            elif val == max_val:
                maxes.append(a)
            else:
                max_val = val
                maxes = [a]
        i = random.randrange(len(maxes))
        return maxes[i]

    def state_value(self, s):
        if self._state_value is None:
            self._state_value = self.reward
        return self._state_value
