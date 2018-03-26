import numpy as np
import copy
import random
import bisect

class RState:
    def __init__(self, field, color, movement):
        self.wins = 0
        self.games = 0
        self.field = field
        self.color = color
        self.movement = movement

class MonteCarloPlayer:
    def __init__(self, player_color, game_field, rounds):
        self.color = player_color
        self.inv_color = game_field.invcolor(player_color)
        self.field = game_field
        self.rounds = rounds

    def move(self):
        movement = self.analyze()
        self.field.move(movement, self.color)

    def analyze(self):
        next_options = self.field.options(self.color)
        next_options_evals = []
        for n_opt in next_options:
            new_field = copy.deepcopy(self.field)
            new_field.move(n_opt, self.color)
            if new_field.game_over():
                return n_opt
            state = RState(new_field, self.inv_color, n_opt)
            self._play(state, self.rounds)
            next_options_evals.append(state.wins / state.games)
        i_max = np.argmax(next_options_evals)
        print("log: {}, best {}".format(next_options_evals, i_max))
        return next_options[i_max]

    def _play(self, rstate, rounds):
        round = 0
        field = rstate.field
        while round < rounds:
            new_field = copy.deepcopy(field)
            color = rstate.color
            while True:
                p_options = new_field.options(color)
                if len(p_options) > 0:
                    weights = [w.score + 1 for w in p_options]
                    i = self._weighted_choice_b(weights)
                    new_field.move(p_options[i], color)
                if new_field.game_over():
                    if new_field.win(self.color):
                        rstate.wins = rstate.wins + 1
                    rstate.games = rstate.games + 1
                    round = round + 1
                    break
                if p_options == []:
                    if new_field.score[self.color] > new_field.score[self.inv_color]:
                        rstate.wins = rstate.wins + 1
                    rstate.games = rstate.games + 1
                    round = round + 1
                    break
                color = new_field.invcolor(color)

    def _weighted_choice_b(self, weights):
        totals = []
        running_total = 0

        for w in weights:
            running_total += w
            totals.append(running_total)

        rnd = random.random() * running_total
        return bisect.bisect_right(totals, rnd)



