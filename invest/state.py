"""State class for investing"""
from functools import cached_property
import json
import math
import os
import random

from config import deepmind_home, CachedInstance


class State(metaclass=CachedInstance):
    def __init__(self, cash, shares, explore_factor=0.5):
        """
        FIXME: This doesn't work for state, unless state space can somehow be continuous?
        """
        self.cash = cash
        self.shares = shares
        self.explore_factor = explore_factor
        self.data = None
        self.revisions = 0
        self._policy_pdf = None
        self._values = None

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
    def fpath(self):
        return f'{deepmind_home}/invest/states/{self.info}.json'

    @cached_property
    def game_over(self):
        """Is this an end state"""
        return False

    def load_from_cache(self):
        if not os.path.isfile(self.fpath):
            return
        try:
            with open(self.fpath) as fp:
                data = json.load(fp)
        except json.decoder.JSONDecodeError:
            os.remove(self.fpath)
            data = {}
        self.data = data

    @cached_property
    def next_play_states(self):
        """Return list of new states that could be reached from this state, given actions in self.actions"""
        return None

    @cached_property
    def next_plays(self):
        """Array of legal plays remaining"""
        if self.game_over:
            return []
        return []

    @cached_property
    def next_state_values(self):
        vals = []
        return vals

    def next_state_from_play(self, chosen_play):
        return State(self.cash, self.shares, chosen_play)

    @property
    def policy_pdf(self):
        if self._policy_pdf is None:
            self._policy_pdf = self.policy_pdf_uniform
        return self._policy_pdf

    @policy_pdf.setter
    def policy_pdf(self, new_policy_pdf):
        self._policy_pdf = new_policy_pdf

    @cached_property
    def policy_pdf_greedy(self):
        """Choice of next play is always whichever one I rate as most valuable at this time."""
        vals = [1 for val in self.next_state_values]
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

    @cached_property
    def policy_pdf_weighted(self):
        """Don't think I'm using this one currently. ???"""
        calc = [(1 + v) ** math.sqrt(self.revisions + 1) for v in self.next_state_values]
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
            raise ValueError(f'Negative policy value: {revised}')
        if max(revised) > 1:
            raise ValueError(f'Policy value > 1: {revised}' % revised)
        if abs(sum(revised) - 1.0) > 1e-4:
            raise ValueError(f"Policy values don't add to 1: {revised}")
        self.policy_pdf = revised

    def revise_values(self):
        nv = self.next_state_values
        player1_vals = sum([self.policy_pdf[i] * nv[i][0] for i in range(len(self.policy_pdf))])
        self.values = [player1_vals, -player1_vals]

    @cached_property
    def rewards(self):
        """Array of scalar values, one for each player"""
        return 0

    def save_to_cache(self):
        """Write reloadable state info to disk cache"""
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        data = {
            'actions': self.next_plays,
            'next_values': self.next_state_values,
            'policy': self.policy_pdf,
            'revisions': self.revisions,
            'reward': self.rewards,
            'terminal': self.game_over,
            'value': self.values,
        }
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @property
    def values(self):
        if self._values is None:
            self._values = self.rewards
        return self._values

    @values.setter
    def values(self, new_values):
        self._values = new_values
