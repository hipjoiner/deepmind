from tictactoe.player import Player
from tictactoe.state import State


def play():
    players = [
        "dummy",    # Player indexing starts with 1
        Player(0, 'X', auto=True),
        Player(1, 'O', auto=True)
    ]
    state = State()
    print(state, '\n')
    while not state.terminal:
        player = players[state.next_to_play]
        a = player.action(state)
        print('%s action: %d\n' % (player, a))
        state = state.apply_action(a)
        print(state, '\n')
    if state.winner:
        print('%s wins.' % players[state.winner])
    else:
        print('Draw.')


if __name__ == '__main__':
    play()

    for t, s in State.cache.items():
        s.save()
