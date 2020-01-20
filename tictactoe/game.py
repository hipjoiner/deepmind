from tictactoe.player import Player
from tictactoe.state import State


class Game:
    def __init__(self):
        self.players = [
            Player(1, name='X', auto=True),
            # Player(2, name='O')
            Player(2, name='O', auto=True)
        ]

    def play(self):
        state = State()
        print(state)
        while not state.terminal:
            p = state.next_to_play
            player = self.players[p - 1]
            a = player.action(state)
            print('%s chooses %d\n' % (player, a))
            state = state.apply_action(p, a)
            print(state)
        if state.winner:
            print('%s wins.' % self.players[state.winner - 1])
        else:
            print('Draw.')


if __name__ == '__main__':
    game = Game()
    game.play()

    print('Passed thru these states:')
    for t, s in State.cache.items():
        print(s.brief())
        s.save()
