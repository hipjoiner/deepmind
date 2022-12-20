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


def run_trial(players, explore_factor):
    state = State(explore_factor=explore_factor)
    state.revise()
    while not state.game_over:
        player = players[state.who_plays_next]
        if not player.auto:
            play = int(input('%s move? ' % player.symbol))
        else:
            play = state.choose_play()
        state = state.apply_play(play)
        state.revise()
    return state.who_won


if __name__ == '__main__':
    trials = 10000
    players = [
        Player('X', number=0, auto=True),
        Player('O', number=1, auto=True),
    ]
    wins = [0, 0]
    for t in range(1, trials + 1):
        winner = run_trial(players, explore_factor=0.0)
        if winner is not None:
            wins[winner] += 1
        if t % 200 == 0:
            log('%d trials:  %d X wins, %d O wins, %d draws.' % (t, wins[0], wins[1], t - (wins[0] + wins[1])))
