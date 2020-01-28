from functools import lru_cache
import json
import math
import os
import random

from tictactoe import config

"""
    0|1|2
    -----
    3|4|5
    -----
    6|7|8
"""

state_dir = '%s/states' % config.home
os.makedirs(state_dir, exist_ok=True)

winners = (
    {0, 1, 2},
    {3, 4, 5},
    {6, 7, 8},
    {0, 3, 6},
    {1, 4, 7},
    {2, 5, 8},
    {0, 4, 8},
    {2, 4, 6},
)


class Unique(type):
    cache = {}

    def __call__(cls, board=(None, None, None, None, None, None, None, None, None)):
        if board not in cls.cache:
            cls.cache[board] = type.__call__(cls, board)
        return cls.cache[board]


class State(metaclass=Unique):
    explore_factor = 0.5

    def __init__(self, board=(None, None, None, None, None, None, None, None, None)):
        self.board = board
        self.data = {'board': board}
        self._policy = None
        self._value = None
        self.revisions = 0
        if os.path.isfile(self.fpath):
            with open(self.fpath) as fp:
                self.data = json.load(fp)
            self._policy = self.data.get('policy', None)
            self._value = self.data.get('value', None)
            self.revisions = self.data.get('revisions', 0)

    def __repr__(self):
        """Show board, actions, next_to_play, reward, terminal, winner"""
        return '\n'.join([
            '%s   %s to play' % (
                '|'.join([' %s ' % self.symbol(i) for i in self.board[0:3]]),
                self.symbol(self.next_to_play),
            ),
            '%s   Actions: %s' % (
                '-----------',
                self.actions,
            ),
            '%s   Values: %s' % (
                '|'.join([' %s ' % self.symbol(i) for i in self.board[3:6]]),
                self.next_values,
            ),
            '%s   Policy: %s' % (
                '-----------',
                self.policy,
            ),
            '%s   Value: %s | Revisions: %d' % (
                '|'.join([' %s ' % self.symbol(i) for i in self.board[6:9]]),
                self.value,
                self.revisions,
            ),
            ''
        ])

    def action(self):
        """Choose and return action a"""
        p = self.policy
        if not p:
            return None
        rnd = random.uniform(0, 1)
        cdf = 0
        for i, prob in enumerate(p):
            cdf += prob
            if rnd <= cdf:
                return self.actions[i]
        return self.actions[-1]

    @property
    @lru_cache()
    def actions(self):
        if self.terminal:
            return []
        return [i for i in range(len(self.board)) if self.board[i] is None]

    def apply_action(self, a):
        """Apply action a to current state and return resulting state
        a is an integer, 0-8, denoting which cell on the board to take
        """
        b = list(self.board)
        b[a] = self.next_to_play
        return State(tuple(b))

    @property
    @lru_cache()
    def fpath(self):
        fname = ''.join([self.symbol(i) for i in self.board])
        fpath = '%s/%s.json' % (state_dir, fname)
        return fpath

    @property
    @lru_cache()
    def last_to_play(self):
        if self.plays == 0:
            return None
        return 1 - self.plays % 2

    @property
    @lru_cache()
    def next_states(self):
        """Return list of new states that could be reached from this state, given actions in self.actions"""
        return [self.apply_action(a) for a in self.actions]

    @property
    @lru_cache()
    def next_to_play(self):
        if self.terminal:
            return None
        return self.plays % 2

    @property
    def next_values(self):
        vals = [self.next_states[i].value for i in range(len(self.next_states))]
        return vals

    @property
    @lru_cache()
    def plays(self):
        """Return total number of plays made up to this state"""
        return len(self.position(0)) + len(self.position(1))

    @property
    def policy(self):
        """Return a list of probabilities of choosing an action over all actions.
        Initial value is uniformly distributed pdf across all actions.
        """
        if self._policy is None:
            self._policy = self.uniform_policy
        return self._policy

    @policy.setter
    def policy(self, val):
        self._policy = val

    @lru_cache()
    def position(self, p):
        """Return a set of all places on the board currently occupied by p
        p is an integer, 1 or 2, denoting player
        """
        return {i for i in range(len(self.board)) if self.board[i] == p}

    def revise(self):
        if self.terminal:
            return
        self.revise_policy()
        self.revise_value()
        self.revisions += 1
        self.save()

    @property
    def greedy_policy(self):
        vals = [val[self.next_to_play] for val in self.next_values]
        max_val = max(vals)
        greedy = [1 if val == max_val else 0 for val in vals]
        max_count = sum(greedy)
        greedy = [val / max_count for val in greedy]
        return greedy

    @property
    def weighted_policy(self):
        calc = [(v + 1) ** math.sqrt(self.revisions + 1) for v in self.next_values]
        norm = sum(calc)
        if norm == 0:
            return
        weighted = [calc[i] / norm for i in range(len(calc))]
        return weighted

    @property
    @lru_cache()
    def uniform_policy(self):
        if not self.actions:
            return []
        uniform = [1 / len(self.actions)] * len(self.actions)
        return uniform

    def revise_policy(self):
        # FIXME: How we change policy probabilities appears to be extremely important to how
        # states are explored.  Look more carefully at these values, and algorithm for revising them.
        greedy = self.greedy_policy
        uniform = self.uniform_policy
        revised = [
            greedy[i] * (1 - State.explore_factor) + uniform[i] * State.explore_factor for i in range(len(self.policy))
        ]
        if min(revised) < 0:
            raise ValueError('Neative policy value: %s' % revised)
        if max(revised) > 1:
            raise ValueError('Policy value > 1: %s' % revised)
        if abs(sum(revised) - 1.0) > 1e-4:
            raise ValueError('Policy values don\'t add to 1: %s' % revised)
        self.policy = revised

    def revise_value(self):
        nv = self.next_values
        val = sum([self.policy[i] * nv[i][0] for i in range(len(self.policy))])
        self.value = [val, -val]

    @property
    @lru_cache()
    def reward(self):
        """Scalar value, from point of view of last to play"""
        if self.winner is not None:
            if self.winner == 0:
                return [1, -1]
            return [-1, 1]
        return [0, 0]

    def save(self):
        data = {
            'actions': self.actions,
            'board': self.board,
            'last_to_play': self.last_to_play,
            'next_to_play': self.next_to_play,
            'next_values': self.next_values,
            'policy': self.policy,
            'revisions': self.revisions,
            'reward': self.reward,
            'terminal': self.terminal,
            'value': self.value,
            'winner': self.winner,
        }
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def symbol(p):
        if p is None:
            return '-'
        return ['X', 'O'][p]

    @property
    @lru_cache()
    def terminal(self):
        if self.winner is not None:
            return True
        return self.plays == 9

    @property
    def value(self):
        if self._value is None:
            self._value = self.reward
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    @lru_cache()
    def winner(self):
        for player in [0, 1]:
            pos = self.position(player)
            for w in winners:
                if w.issubset(pos):
                    return player
        return None
