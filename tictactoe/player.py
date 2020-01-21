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
        """
        # Simplest policy: choose at random from available actions
        i = random.randrange(len(s.actions))
        return s.actions[i]
        """

        # Next simplest:  if we see a state we can move to and win (max value), take it
        max_val = -1
        maxes = []
        for a in s.actions:
            s_prime = s.transitions[a]
            val = s_prime.state_value(s.next_to_play)
            if val < max_val:
                continue
            elif val == max_val:
                maxes.append(a)
            else:
                max_val = val
                maxes = [a]
        i = random.randrange(len(maxes))
        return maxes[i]
