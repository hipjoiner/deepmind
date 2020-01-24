from functools import lru_cache
import json
import os

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

symbol = ('-', 'X', 'O')

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

    def __call__(cls, board=(0, 0, 0, 0, 0, 0, 0, 0, 0)):
        if board not in cls.cache:
            cls.cache[board] = type.__call__(cls, board)
        return cls.cache[board]


class State(metaclass=Unique):
    def __init__(self, board=(0, 0, 0, 0, 0, 0, 0, 0, 0)):
        self.board = board
        if os.path.isfile(self.fpath):
            self.load()

    def __repr__(self):
        """Show board, actions, next_to_play, reward, terminal, winner"""
        l1 = '%s   Reward: %s' % (
            '|'.join([' %s ' % symbol[i] for i in self.board[0:3]]),
            self.reward
        )
        l2 = '%s   Terminal: %s' % (
            '-----------',
            self.terminal
        )
        l3 = '%s   Actions: %s' % (
            '|'.join([' %s ' % symbol[i] for i in self.board[3:6]]),
            self.actions
        )
        l4 = '%s   Winner: %s' % (
            '-----------',
            self.winner
        )
        l5 = '%s   Next to play: %s' % (
            '|'.join([' %s ' % symbol[i] for i in self.board[6:9]]),
            self.next_to_play
        )
        return '\n'.join([l1, l2, l3, l4, l5])

    @property
    @lru_cache()
    def actions(self):
        if self.terminal:
            return []
        return [i for i in range(len(self.board)) if self.board[i] == 0]

    def apply_action(self, a):
        """Apply action a to current state and return resulting state
        a is an integer, 0-8, denoting which cell on the board to take
        """
        b = list(self.board)
        b[a] = self.next_to_play
        return State(tuple(b))

    def brief(self):
        return '|'.join([symbol[i] for i in self.board])

    @property
    @lru_cache()
    def fpath(self):
        fname = ''.join([symbol[i] for i in self.board])
        fpath = '%s/%s.json' % (state_dir, fname)
        return fpath

    def load(self):
        with open(self.fpath) as fp:
            data = json.load(fp)

    @property
    @lru_cache()
    def next_to_play(self):
        if self.terminal:
            return 0
        return 1 + (len(self.position(1)) - len(self.position(2)))

    @lru_cache()
    def position(self, p):
        """Return a set of all places on the board currently occupied by p
        p is an integer, 1 or 2, denoting player
        """
        return {i for i in range(len(self.board)) if self.board[i] == p}

    @property
    @lru_cache()
    def reward(self):
        """Array of rewards by player"""
        if not self.winner:
            return [0, 0]
        if self.winner == 1:
            return [1, -1]
        return [-1, 1]

    def save(self):
        data = {
            'board': self.board,
            'next_to_play': self.next_to_play,
            'actions': self.actions,
            'reward': self.reward,
            'terminal': self.terminal,
            'winner': self.winner,
        }
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @property
    @lru_cache()
    def terminal(self):
        return self.winner is not None

    @property
    @lru_cache()
    def transitions(self):
        return {a: self.apply_action(self.next_to_play, a) for a in self.actions}

    @property
    @lru_cache()
    def winner(self):
        for player in [1, 2]:
            pos = self.position(player)
            for w in winners:
                if w.issubset(pos):
                    return player
        if 0 not in self.board:
            return 0
        return None
