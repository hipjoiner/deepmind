from functools import lru_cache
import json
import os

"""
    0|1|2
    -----
    3|4|5
    -----
    6|7|8
"""

state_dir = 'C:/deepmind/tictactoe/states'
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
        else:
            print('Found in cache')
        return cls.cache[board]


class State(metaclass=Unique):
    def __init__(self, board=(0, 0, 0, 0, 0, 0, 0, 0, 0)):
        self._board = board
        self._actions = None
        self._next_to_play = None
        self._reward = None
        self._terminal = None
        self._winner = -1       # For winner, None is a meaningful computed value, so use -1 to mean "not computed yet"
        # If cached in file, load additional data
        if os.path.isfile(self.fpath()):
            print('Found file cache')
            self.load()
        # In future we'll load more than just board state: saved value estimates, etc.

    def __repr__(self):
        return '\n'.join([
            '|'.join([' %s ' % symbol[i] for i in self.board[0:3]]),
            '-----------',
            '|'.join([' %s ' % symbol[i] for i in self.board[3:6]]),
            '-----------',
            '|'.join([' %s ' % symbol[i] for i in self.board[6:9]])
        ])

    @property
    def actions(self):
        if self._actions is None:
            self._actions = [i for i in range(len(self.board)) if self.board[i] == 0]
        return self._actions

    @actions.setter
    def actions(self, val):
        self._actions = val

    def apply_action(self, p, a):
        if a not in self.actions:
            raise ValueError('Illegal action %d by %s' % (a, p))
        b = list(self.board)
        b[a] = p
        return State(tuple(b))

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, val):
        self._board = val

    def brief(self):
        return '|'.join([symbol[i] for i in self.board])

    @lru_cache()
    def fpath(self):
        fname = ''.join([symbol[i] for i in self.board])
        fpath = '%s/%s.json' % (state_dir, fname)
        return fpath

    def load(self):
        print('Loading %s...' % str(self.board))
        with open(self.fpath()) as fp:
            data = json.load(fp)
        self.actions = data.get('actions', None)
        self.board = data.get('board', None)
        self.next_to_play = data.get('next_to_play', None)
        self.reward = data.get('reward', None)
        self.terminal = data.get('terminal', None)
        self.winner = data.get('winner', -1)

    @property
    def next_to_play(self):
        if self._next_to_play is None:
            if self.terminal:
                self._next_to_play = 0
            else:
                p1 = self.position(1)
                p2 = self.position(2)
                if len(p1) <= len(p2):
                    self._next_to_play = 1
                else:
                    self._next_to_play = 2
        return self._next_to_play

    @next_to_play.setter
    def next_to_play(self, val):
        self._next_to_play = val

    def position(self, p):
        return {i for i in range(len(self.board)) if self.board[i] == p}

    @property
    def reward(self):
        """Array of rewards by player"""
        if self._reward is None:
            if not self.winner:
                self._reward = [0, 0]
            elif self.winner == 1:
                self._reward = [1, -1]
            else:
                self._reward = [-1, 1]
        return self._reward

    @reward.setter
    def reward(self, val):
        self._reward = val

    def save(self):
        data = {
            'board': self.board,
            'next_to_play': self.next_to_play,
            'actions': self.actions,
            'reward': self.reward,
            'terminal': self.terminal,
            'winner': self.winner,
        }
        with open(self.fpath(), 'w') as fp:
            json.dump(data, fp, indent=4)

    @property
    def terminal(self):
        if self._terminal is None:
            self._terminal = self.winner is not None
        return self._terminal

    @terminal.setter
    def terminal(self, val):
        self._terminal = val

    @property
    def winner(self):
        if self._winner == -1:
            for player in [1, 2]:
                pos = self.position(player)
                for w in winners:
                    if w.issubset(pos):
                        self._winner = player
                        break
                if self._winner:
                    break
            if self._winner == -1:
                if 0 not in self.board:
                    self._winner = 0
                else:
                    self._winner = None
        return self._winner

    @winner.setter
    def winner(self, val):
        self._winner = val
