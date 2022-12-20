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


def play(players):
    state = State()
    state.revise()
    while not state.terminal:
        player = players[state.next_to_play]
        if not player.auto:
            a = int(input('%s move? ' % player.symbol))
        else:
            a = state.action()
        state = state.apply_action(a)
        state.revise()
    return state.winner


if __name__ == '__main__':
    trials = 10000
    State.explore_factor = 0.0
    players = [
        Player('X', number=0, auto=True),
        Player('O', number=1, auto=True),
    ]
    wins = [0, 0]
    for t in range(1, trials + 1):
        winner = play(players)
        if winner is not None:
            wins[winner] += 1
        if t % 200 == 0:
            log('%d trials:  %d X wins, %d O wins, %d draws.' % (t, wins[0], wins[1], t - (wins[0] + wins[1])))
