"""State class for tic tac toe.

TODO:
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
from player import Player


# Winning board positions
winning_positions = (
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
    def __init__(self, player1, player2, board=None, explore_factor=0.5):
        self.players = [
            player1,
            player2
        ]
        self.no_one = Player('-')
        self.board = board
        if self.board is None:
            self.board = tuple([self.no_one] * 9)
        self.explore_factor = explore_factor
        self.fpath = f"{deepmind_home}/states/{''.join([p.symbol for p in self.board])}.json"
        self.policy_pdf = self.policy_pdf_uniform
        self.values = self.rewards
        self.revisions = 0
        self.load_from_cache()

    def choose_play(self):
        """Choose and return a play from available options"""
        if not self.policy_pdf:
            return None
        rnd = random.uniform(0, 1)
        cdf = 0
        for i, prob in enumerate(self.policy_pdf):
            cdf += prob
            if rnd <= cdf:
                return self.next_plays[i]
        return self.next_plays[-1]

    @cached_property
    def detail(self):
        """Show board, actions, next_to_play, reward, terminal, winner"""
        return '\n'.join([
            '%s   %s to play' % (
                '|'.join([' %s ' % p.symbol for p in self.board[0:3]]),
                self.who_plays_next.symbol,
            ),
            '%s   Actions: %s' % (
                '-----------',
                self.next_plays,
            ),
            '%s   Values: %s' % (
                '|'.join([' %s ' % p.symbol for p in self.board[3:6]]),
                self.next_state_values,
            ),
            '%s   Policy: %s' % (
                '-----------',
                self.policy_pdf,
            ),
            '%s   Value: %s | Revisions: %d' % (
                '|'.join([' %s ' % p.symbol for p in self.board[6:9]]),
                self.values,
                self.revisions,
            ),
            ''
        ])

    @cached_property
    def game_over(self):
        """Is this an end state"""
        if self.who_won != self.no_one:
            return True
        return self.total_play_count == 9

    def load_from_cache(self):
        if not os.path.isfile(self.fpath):
            return
        with open(self.fpath) as fp:
            data = json.load(fp)
        self.policy_pdf = data.get('policy', self.policy_pdf_uniform)
        self.values = data.get('value', self.rewards)
        self.revisions = data.get('revisions', 0)

    @cached_property
    def next_play_states(self):
        """Return list of new states that could be reached from this state, given actions in self.actions"""
        return [self.next_state_from_play(play) for play in self.next_plays]

    @cached_property
    def next_plays(self):
        """Array of legal plays remaining"""
        if self.game_over:
            return []
        return [i for i in range(len(self.board)) if self.board[i] == self.no_one]

    @property
    def next_state_values(self):
        # vals = [self.next_states[i].value for i in range(len(self.next_states))]
        vals = [state.values for state in self.next_play_states]
        return vals

    def next_state_from_play(self, chosen_play):
        """Apply action a to current state and return resulting state
        a is an integer, 0-8, denoting which cell on the board to take
        """
        board = list(self.board)
        board[chosen_play] = self.who_plays_next
        return State(self.players[0], self.players[1], board=tuple(board), explore_factor=self.explore_factor)

    @cache
    def player_position(self, player):
        """Return a set of all places on the board currently occupied by player
            player is an integer
        """
        return {i for i in range(len(self.board)) if self.board[i] == player}

    @property
    def policy_pdf_greedy(self):
        """Choice of next play is always whichever one I rate as most valuable at this time."""
        vals = [val[self.who_plays_next.number] for val in self.next_state_values]
        max_val = max(vals)
        greedy_pdf = [1 if val == max_val else 0 for val in vals]
        max_count = sum(greedy_pdf)
        greedy_pdf = [val / max_count for val in greedy_pdf]
        return greedy_pdf

    @cached_property
    def policy_pdf_uniform(self):
        """Choice of next play is uniformly random across available options."""
        if not self.next_plays:
            return []
        uniform_pdf = [1 / len(self.next_plays)] * len(self.next_plays)
        return uniform_pdf

    @property
    def policy_pdf_weighted(self):
        """Don't think I'm using this one currently. ???"""
        calc = [(v + 1) ** math.sqrt(self.revisions + 1) for v in self.next_state_values]
        norm = sum(calc)
        if norm == 0:
            return
        weighted_pdf = [calc[i] / norm for i in range(len(calc))]
        return weighted_pdf

    def revise(self):
        if self.game_over:
            return
        self.revise_policy_pdf()
        self.revise_values()
        self.revisions += 1
        self.save_to_cache()

    def revise_policy_pdf(self):
        greedy = self.policy_pdf_greedy
        uniform = self.policy_pdf_uniform
        revised = [
            greedy[i] * (1 - self.explore_factor) + uniform[i] * self.explore_factor for i in range(len(self.policy_pdf))
        ]
        if min(revised) < 0:
            raise ValueError('Neative policy value: %s' % revised)
        if max(revised) > 1:
            raise ValueError('Policy value > 1: %s' % revised)
        if abs(sum(revised) - 1.0) > 1e-4:
            raise ValueError('Policy values don\'t add to 1: %s' % revised)
        self.policy_pdf = revised

    def revise_values(self):
        nv = self.next_state_values
        player1_vals = sum([self.policy_pdf[i] * nv[i][0] for i in range(len(self.policy_pdf))])
        self.values = [player1_vals, -player1_vals]

    @cached_property
    def rewards(self):
        """Array of scalar values, one for each player"""
        if self.who_won == self.no_one:
            return [0, 0]
        elif self.who_won == self.players[0]:
            return [1, -1]
        else:
            return [-1, 1]

    def save_to_cache(self):
        """Write reloadable state info to disk cache"""
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        data = {
            'actions': self.next_plays,
            'board': [player.number for player in self.board],
            'last_to_play': self.who_played_last.number,
            'next_to_play': self.who_plays_next.number,
            'next_values': self.next_state_values,
            'policy': self.policy_pdf,
            'revisions': self.revisions,
            'reward': self.rewards,
            'terminal': self.game_over,
            'value': self.values,
            'winner': self.who_won.number,
        }
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @cached_property
    def total_play_count(self):
        """Return total number of plays made up to this state"""
        # return len(self.player_position(0)) + len(self.player_position(1))
        return sum([len(self.player_position(player)) for player in self.players])

    @cached_property
    def who_played_last(self):
        """Player who made last play to reach this state"""
        if self.total_play_count == 0:
            return self.no_one
        return self.players[1 - self.total_play_count % 2]

    @cached_property
    def who_plays_next(self):
        """Player who gets next play"""
        if self.game_over:
            return self.no_one
        return self.players[self.total_play_count % 2]

    @cached_property
    def who_won(self):
        """Winner of the game, if there is one:
            0 or 1      Player that won
            None        Draw, or game not over (distinguish between these by checking self.terminal)
        """
        for player in self.players:
            for winner in winning_positions:
                if self.player_position(player).issuperset(winner):
                    return player
        return self.no_one
