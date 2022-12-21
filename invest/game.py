"""
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


def run_many(trials):
    info = 1
    s0 = State(info)
    wins = [0, 0]
    for t in range(1, trials + 1):
        state = run_trial(s0)
        if state.who_won is not state.no_one:
            wins[state.who_won.number] += 1
        if t % 200 == 0:
            log('%d trials:  %d X wins, %d O wins, %d draws.' % (t, wins[0], wins[1], t - (wins[0] + wins[1])))


if __name__ == '__main__':
    run_many(30000)
