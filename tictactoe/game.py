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


if __name__ == '__main__':
    trials = 10000
    State.explore_factor = 0.1
    players = [
        Player('X', auto=True),
        Player('O', auto=True),
    ]
    for i in range(trials):
        print('\nTrial #%d\n' % (i + 1))
        play(players)
