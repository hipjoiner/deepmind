from tictactoe.player import Player
from tictactoe.state import State


class Game:
    def __init__(self):
        self.players = [
            Player(0, 'X', auto=True),
            Player(1, 'O', auto=True)
        ]

    def play(self):
        state = State()
        print(state, '\n')
        while not state.terminal:
            p = state.next_to_play
            player = self.players[p - 1]
            a = player.policy(state)
            print('%s action: %d\n' % (player, a))
            state = state.apply_action(a)
            print(state, '\n')
        if state.winner:
            print('%s wins.' % self.players[state.winner - 1])
        else:
            print('Draw.')


if __name__ == '__main__':
    game = Game()
    game.play()

    for t, s in State.cache.items():
        s.save()
