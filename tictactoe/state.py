"""
State class for tic tac toe.
Loose ends:

    exploration factor implementation is very kludgy
    no discount factor capability yet
    game play vs. game training is also kludgy; clean up
    this effectively uses a 1-step lookahead algorithm (TD0?)
        how to extend to use n-step-- TD-lambda(?) ?
        see David Silver's lecture 6 on value function approximation & gradient descent

Board representation:
    0|1|2
    -----
    3|4|5
    -----
    6|7|8
"""
from functools import cache, cached_property
import json
import math
import os
import random

from config import deepmind_home, CachedInstance


# Winning board positions
winners = (
    {0, 1, 2},      # Across
    {3, 4, 5},
    {6, 7, 8},
    {0, 3, 6},      # Down
    {1, 4, 7},
    {2, 5, 8},
    {0, 4, 8},      # Diagonal
    {2, 4, 6},
)


class State(metaclass=CachedInstance):
    def __init__(self, board=None, explore_factor=0.5):
        self.board = board
        if self.board is None:
            self.board = (None, None, None, None, None, None, None, None, None)
        self.explore_factor = explore_factor
        self.data = {'board': board}
        self._policy = None
        self._values = None
        self.revisions = 0
        if os.path.isfile(self.fpath):
            with open(self.fpath) as fp:
                self.data = json.load(fp)
            self._policy = self.data.get('policy', None)
            self._values = self.data.get('value', None)
            self.revisions = self.data.get('revisions', 0)

    def apply_play(self, chosen_spot):
        """Apply action a to current state and return resulting state
        a is an integer, 0-8, denoting which cell on the board to take
        """
        board = list(self.board)
        board[chosen_spot] = self.who_plays_next
        return State(board=tuple(board), explore_factor=self.explore_factor)

    def choose_play(self):
        """Choose and return action a"""
        if not self.policy:
            return None
        rnd = random.uniform(0, 1)
        cdf = 0
        for i, prob in enumerate(self.policy):
            cdf += prob
            if rnd <= cdf:
                return self.possible_next_plays[i]
        return self.possible_next_plays[-1]

    @cached_property
    def detail(self):
        """Show board, actions, next_to_play, reward, terminal, winner"""
        return '\n'.join([
            '%s   %s to play' % (
                '|'.join([' %s ' % self.symbol(i) for i in self.board[0:3]]),
                self.symbol(self.who_plays_next),
            ),
            '%s   Actions: %s' % (
                '-----------',
                self.possible_next_plays,
            ),
            '%s   Values: %s' % (
                '|'.join([' %s ' % self.symbol(i) for i in self.board[3:6]]),
                self.next_play_state_values,
            ),
            '%s   Policy: %s' % (
                '-----------',
                self.policy,
            ),
            '%s   Value: %s | Revisions: %d' % (
                '|'.join([' %s ' % self.symbol(i) for i in self.board[6:9]]),
                self.values,
                self.revisions,
            ),
            ''
        ])

    @cached_property
    def fpath(self):
        fname = ''.join([self.symbol(i) for i in self.board])
        return f'{deepmind_home}/states/{fname}.json'

    @cached_property
    def game_over(self):
        """Is this an end state"""
        if self.who_won is not None:
            return True
        return self.total_play_count == 9

    @property
    def next_play_state_values(self):
        # vals = [self.next_states[i].value for i in range(len(self.next_states))]
        vals = [state.values for state in self.possible_next_play_states]
        return vals

    @cache
    def player_position(self, player):
        """Return a set of all places on the board currently occupied by player
            player is an integer
        """
        return {i for i in range(len(self.board)) if self.board[i] == player}

    @property
    def policy(self):
        """Policy is a list of probabilities of choosing a play over all possible."""
        if self._policy is None:
            self._policy = self.policy_uniform
        return self._policy

    @policy.setter
    def policy(self, val):
        self._policy = val

    @property
    def policy_greedy(self):
        vals = [val[self.who_plays_next] for val in self.next_play_state_values]
        max_val = max(vals)
        greedy = [1 if val == max_val else 0 for val in vals]
        max_count = sum(greedy)
        greedy = [val / max_count for val in greedy]
        return greedy

    @cached_property
    def policy_uniform(self):
        """Choice of next play is uniformly random across available options."""
        if not self.possible_next_plays:
            return []
        uniform = [1 / len(self.possible_next_plays)] * len(self.possible_next_plays)
        return uniform

    @property
    def policy_weighted(self):
        calc = [(v + 1) ** math.sqrt(self.revisions + 1) for v in self.next_play_state_values]
        norm = sum(calc)
        if norm == 0:
            return
        weighted = [calc[i] / norm for i in range(len(calc))]
        return weighted

    @cached_property
    def possible_next_play_states(self):
        """Return list of new states that could be reached from this state, given actions in self.actions"""
        return [self.apply_play(a) for a in self.possible_next_plays]

    @cached_property
    def possible_next_plays(self):
        """Array of legal plays remaining"""
        if self.game_over:
            return []
        return [i for i in range(len(self.board)) if self.board[i] is None]

    def revise(self):
        if self.game_over:
            return
        self.revise_policy()
        self.revise_values()
        self.revisions += 1
        self.save()

    def revise_policy(self):
        greedy = self.policy_greedy
        uniform = self.policy_uniform
        revised = [
            greedy[i] * (1 - self.explore_factor) + uniform[i] * self.explore_factor for i in range(len(self.policy))
        ]
        if min(revised) < 0:
            raise ValueError('Neative policy value: %s' % revised)
        if max(revised) > 1:
            raise ValueError('Policy value > 1: %s' % revised)
        if abs(sum(revised) - 1.0) > 1e-4:
            raise ValueError('Policy values don\'t add to 1: %s' % revised)
        self.policy = revised

    def revise_values(self):
        nv = self.next_play_state_values
        val = sum([self.policy[i] * nv[i][0] for i in range(len(self.policy))])
        self.values = [val, -val]

    @cached_property
    def rewards(self):
        """Array of scalar values, one for each player"""
        if self.who_won is not None:
            if self.who_won == 0:
                return [1, -1]
            return [-1, 1]
        return [0, 0]

    def save(self):
        """Write reloadable state info to disk cache"""
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        data = {
            'actions': self.possible_next_plays,
            'board': self.board,
            'last_to_play': self.who_played_last,
            'next_to_play': self.who_plays_next,
            'next_values': self.next_play_state_values,
            'policy': self.policy,
            'revisions': self.revisions,
            'reward': self.rewards,
            'terminal': self.game_over,
            'value': self.values,
            'winner': self.who_won,
        }
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def symbol(player):
        if player is None:
            return '-'
        return ['X', 'O'][player]

    @cached_property
    def total_play_count(self):
        """Return total number of plays made up to this state"""
        return len(self.player_position(0)) + len(self.player_position(1))

    @property
    def values(self):
        """Array of scalar values, one for each player"""
        if self._values is None:
            self._values = self.rewards
        return self._values

    @values.setter
    def values(self, new_values):
        """Array of scalar values, one for each player"""
        self._values = new_values

    @cached_property
    def who_played_last(self):
        if self.total_play_count == 0:
            return None
        return 1 - self.total_play_count % 2

    @cached_property
    def who_plays_next(self):
        if self.game_over:
            return None
        return self.total_play_count % 2

    @cached_property
    def who_won(self):
        """Winner of the game, if there is one:
            0 or 1      Player that won
            None        Draw, or game not over (distinguish between these by checking self.terminal)
        """
        for player in [0, 1]:
            pos = self.player_position(player)
            for w in winners:
                if w.issubset(pos):
                    return player
        return None
