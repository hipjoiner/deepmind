"""
Game play versus training is messy here.  Create separate entry points or options to cover:

    Training (specify number of rounds or time to train)
    Play vs machine (specify human player)

    Later option for either training or human play could specify starting state (default to standard game start)

    Clear training data

"""
from tictactoe.state import State


class Player:
    def __init__(self, symbol, auto=True):
        self.symbol = symbol
        self.auto = auto


def play(players):
    state = State()
    state.revise()
    print(state)
    while not state.terminal:
        player = players[state.next_to_play]
        if not player.auto:
            a = int(input('%s move? ' % player.symbol))
        else:
            a = state.action()
            print('%s action: %d\n' % (player.symbol, a))
        state = state.apply_action(a)
        state.revise()
        print(state)
    if state.winner is not None:
        print('%s wins.' % players[state.winner].symbol)
    else:
        print('Draw.')
    return state.winner


if __name__ == '__main__':
    trials = 10000
    State.explore_factor = 0.0
    players = [
        Player('X', auto=True),
        Player('O', auto=True),
    ]
    wins = [0, 0]
    for i in range(trials):
        print('\nTrial #%d\n' % (i + 1))
        winner = play(players)
        if winner is not None:
            wins[winner] += 1
        print('After %d trials:  %d X wins, %d O wins, %d draws.' % (i + 1, wins[0], wins[1], i + 1 - (wins[0] + wins[1])))