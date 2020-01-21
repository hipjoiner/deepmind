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

"""
Transition probability function:
    What are s-prime states
    What probability of each s-prime?

State value function:  what is the value of this state?
    Depends on policy function

Action value function:  what is value of action a?
    Depends on Player policy function, but only after action:
        Take action a
        Determine new state(s) s-prime
        Use state value fn to evaluate values of s-prime states

Player policy function:  what action should we take?
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
            # print('Added to cache: %s' % str(board))
        # else:
            # print('Found in cache: %s' % str(board))
        return cls.cache[board]


class State(metaclass=Unique):
    def __init__(self, board=(0, 0, 0, 0, 0, 0, 0, 0, 0)):
        self._board = board
        self._actions = None
        self._next_to_play = None
        self._rewards = None
        self._terminal = None
        self._transitions = None
        self._winner = -1       # For winner, None is a meaningful computed value, so use -1 to mean "not computed yet"
        # If cached in file, load additional data
        if os.path.isfile(self.fpath):
            # print('Loading %s from file %s...\n' % (self.board, self.fpath))
            self.load()
        # In future we'll load more than just board state: saved value estimates, etc.

    def __repr__(self):
        """Also show actions, next_to_play, reward, terminal, winner
        """
        l1 = '%s   Actions: %s  Values: %s' % (
            '|'.join([' %s ' % symbol[i] for i in self.board[0:3]]),
            self.actions,
            self.action_values
        )
        l2 = '%s   Next to play: %s' % (
            '-----------',
            self.next_to_play
        )
        l3 = '%s   Reward: %s' % (
            '|'.join([' %s ' % symbol[i] for i in self.board[3:6]]),
            self.rewards
        )
        l4 = '%s   Terminal: %s' % (
            '-----------',
            self.terminal
        )
        l5 = '%s   Winner: %s' % (
            '|'.join([' %s ' % symbol[i] for i in self.board[6:9]]),
            self.winner
        )
        return '\n'.join([l1, l2, l3, l4, l5])

    def action_value(self, a):
        return self.transitions[a].state_value(self.next_to_play)

    @property
    def action_values(self):
        return [self.transitions[a].state_value(self.next_to_play) for a in self.actions]

    @property
    def actions(self):
        if self._actions is None:
            if self.terminal:
                self._actions = []
            else:
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

    @property
    @lru_cache()
    def fpath(self):
        fname = ''.join([symbol[i] for i in self.board])
        fpath = '%s/%s.json' % (state_dir, fname)
        return fpath

    def load(self):
        with open(self.fpath) as fp:
            data = json.load(fp)
        self.actions = data.get('actions', None)
        self.board = data.get('board', None)
        self.next_to_play = data.get('next_to_play', None)
        self.rewards = data.get('rewards', None)
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

    def reward(self, player=None):
        if not self.terminal or not player:
            return 0
        return self.rewards[player - 1]

    @property
    def rewards(self):
        """Array of rewards by player"""
        if self._rewards is None:
            if not self.winner:
                self._rewards = [0, 0]
            elif self.winner == 1:
                self._rewards = [1, -1]
            else:
                self._rewards = [-1, 1]
        return self._rewards

    @rewards.setter
    def rewards(self, val):
        self._rewards = val

    def save(self):
        data = {
            'board': self.board,
            'next_to_play': self.next_to_play,
            'actions': self.actions,
            'rewards': self.rewards,
            'terminal': self.terminal,
            'winner': self.winner,
        }
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    def state_value(self, player):
        return self.reward(player)

    @property
    def terminal(self):
        if self._terminal is None:
            self._terminal = self.winner is not None
        return self._terminal

    @terminal.setter
    def terminal(self, val):
        self._terminal = val

    @property
    def transitions(self):
        if self._transitions is None:
            if not self.next_to_play:
                self._transitions = {}
            else:
                self._transitions = {a: self.apply_action(self.next_to_play, a) for a in self.actions}
        return self._transitions

    @transitions.setter
    def transitions(self, val):
        self._transitions = val

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
