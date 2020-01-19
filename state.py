from functools import lru_cache

"""
    0|1|2
    -----
    3|4|5
    -----
    6|7|8
"""

symbol = (' ', 'X', 'O')

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


class State:
    def __init__(self, board=None):
        if board is None:
            board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.board = board

    def __repr__(self):
        return '\n'.join([
            '|'.join([' %s ' % symbol[i] for i in self.board[0:3]]),
            '-----------',
            '|'.join([' %s ' % symbol[i] for i in self.board[3:6]]),
            '-----------',
            '|'.join([' %s ' % symbol[i] for i in self.board[6:9]])
        ])

    def apply_action(self, p, a):
        self.board[a] = p

    def next_to_play(self):
        while not self.terminal():
            p1 = self.position(1)
            p2 = self.position(2)
            if len(p1) <= len(p2):
                yield 1
            else:
                yield 2

    def position(self, p):
        return {i for i in range(len(self.board)) if self.board[i] == p}

    def terminal(self):
        if 0 not in self.board:
            return True
        for p in [1, 2]:
            if self.winner(p):
                return True
        return False

    def winner(self, p):
        pos = self.position(p)
        for w in winners:
            if w.issubset(pos):
                return True
        return False
