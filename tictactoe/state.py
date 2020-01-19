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

state_dir = 'D:/deepmind/tictactoe/states'
os.makedirs(state_dir, exist_ok=True)


class State:
    cache = {}

    @staticmethod
    def get(board=(0, 0, 0, 0, 0, 0, 0, 0, 0)):
        if board not in State.cache:
            if State.loadable(board):
                board = State.load(board)
            State.cache[board] = State(board)
        return State.cache[board]

    @staticmethod
    @lru_cache()
    def fpath(board):
        fname = ''.join([symbol[i] for i in board])
        fpath = '%s/%s.json' % (state_dir, fname)
        return fpath

    @staticmethod
    def load(board):
        print('Loading %s...' % str(board))
        with open(State.fpath(board)) as fp:
            data = json.load(fp)
        # In future we'll load more than just board state: saved value estimates, etc.
        b = tuple(data['board'])
        return b

    @staticmethod
    def loadable(board):
        return os.path.isfile(State.fpath(board))

    def __init__(self, board):
        self.board = board

    def __repr__(self):
        return '\n'.join([
            '|'.join([' %s ' % symbol[i] for i in self.board[0:3]]),
            '-----------',
            '|'.join([' %s ' % symbol[i] for i in self.board[3:6]]),
            '-----------',
            '|'.join([' %s ' % symbol[i] for i in self.board[6:9]])
        ])

    def actions(self, p):
        if self.next_to_play() != p:
            return {}
        return [i for i in range(len(self.board)) if self.board[i] == 0]

    def apply_action(self, p, a):
        if a not in self.actions(p):
            raise ValueError('Illegal action %d by %s' % (a, p))
        b = list(self.board)
        b[a] = p
        return State.get(tuple(b))

    def brief(self):
        return '|'.join([symbol[i] for i in self.board])

    def next_to_play(self):
        if self.terminal():
            return 0
        p1 = self.position(1)
        p2 = self.position(2)
        if len(p1) <= len(p2):
            return 1
        return 2

    def position(self, p):
        return {i for i in range(len(self.board)) if self.board[i] == p}

    def reward(self):
        """Array of rewards by player"""
        w = self.winner()
        if not w:
            return [0, 0]
        if w == 1:
            return [1, -1]
        return [-1, 1]

    def save(self):
        data = {
            'board': self.board
        }
        with open(State.fpath(self.board), 'w') as fp:
            json.dump(data, fp)

    def terminal(self):
        return self.winner() is not None

    @lru_cache()
    def winner(self):
        for p in [1, 2]:
            pos = self.position(p)
            for w in winners:
                if w.issubset(pos):
                    return p
        if 0 not in self.board:
            return 0
        return None
