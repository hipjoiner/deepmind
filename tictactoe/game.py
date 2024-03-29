"""
Game play versus training is messy here.  Create separate entry points or options to cover:

    Training (specify number of rounds or time to train)
    Play vs machine (specify human player)

    Later option for either training or human play could specify starting state (default to standard game start)

    Clear training data
"""
from config import log
from state import State


def run_trial(starting_state):
    state = starting_state
    state.revise()
    while not state.game_over:
        player = state.who_plays_next
        if player.auto:
            play = state.choose_play()
        else:
            play = int(input(f'{player.symbol} move? '))
        state = state.next_state_from_play(play)
        state.revise()
    return state


def run_many(trials, explore_factor):
    s0 = State(cash=10000, shares=0)
    for t in range(1, trials + 1):
        state = run_trial(s0)
        log('Trial {t}: ending value {state.total_value}')


if __name__ == '__main__':
    run_many(30000, explore_factor=0.5)
