"""
Game play versus training is messy here.  Create separate entry points or options to cover:

    Training (specify number of rounds or time to train)
    Play vs machine (specify human player)

    Later option for either training or human play could specify starting state (default to standard game start)

    Clear training data
"""
from config import log
from player import Player
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


def run_many(trials):
    p1 = Player('X', number=0, auto=True)
    p2 = Player('O', number=1, auto=True)
    s0 = State(p1, p2, explore_factor=0.0)
    wins = [0, 0]
    for t in range(1, trials + 1):
        state = run_trial(s0)
        if state.who_won is not state.no_one:
            wins[state.who_won.number] += 1
        if t % 200 == 0:
            log('%d trials:  %d X wins, %d O wins, %d draws.' % (t, wins[0], wins[1], t - (wins[0] + wins[1])))


if __name__ == '__main__':
    run_many(10000)
