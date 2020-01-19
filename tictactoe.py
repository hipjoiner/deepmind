from state import State


class Player:
    def __init__(self, name, auto=False):
        self.name = name
        self.auto = auto

    def action(self, s):
        if self.auto:
            spot = s.board.index(0)
            print('Player %s chooses %d' % (self.name, spot))
            return spot
        spot = input('%s move? ' % self.name)
        return int(spot)


class Game:
    def __init__(self):
        self.state = State()
        self.players = [
            Player('X', auto=True),
            Player('O', auto=True)
        ]

    def play(self):
        for p in self.state.next_to_play():
            player = self.players[p - 1]
            a = player.action(self.state)
            self.state.apply_action(p, a)
            print('Position:')
            print(self.state)


if __name__ == '__main__':
    game = Game()
    game.play()
