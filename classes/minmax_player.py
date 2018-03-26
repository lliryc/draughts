import numpy as np
import copy

class State:
    NINF = -1000
    PINF = 1000
    def __init__(self, field, deep_level, color, state, movement):
        self.alpha = self.NINF
        self.beta = self.PINF
        self.field = field
        self.level = deep_level
        self.color = color
        self.childs = None
        self.child_ix = 0
        self.parent = state
        self.movement = movement
        self.is_root = False

class MinMaxPlayer:
    def __init__(self, player_color, game_field, max_deep):
        self.color = player_color
        self.inv_color = game_field.invcolor(player_color)
        self.field = game_field
        self.deep = max_deep

    def move(self):
        movement = self.analyze()
        self.field.move(movement, self.color)

    def analyze(self):
        root = State(self.field, 1, self.color, None, None)
        root.is_root = True
        stack = [root]

        while len(stack) > 0:
            *stack, state = stack

            if (state.level == self.deep and state.color != self.color) or  (state.field.game_over() == True): #or (state.child_ix == len(state.childs)):
                #stop deep processing, upstream
                score = state.field.score[self.color] -  state.field.score[self.inv_color]
                state.alpha = score
                state.beta = score
                while state.parent is not None:
                    (a0,b0) = state.parent.alpha, state.parent.beta
                    if state.color == self.color and (state.alpha >= state.parent.alpha and state.beta <= state.parent.beta):
                        state.parent.movement = state.movement
                        #print("log: winner step score ({},{})".format(state.field.score[self.color], state.field.score[self.inv_color]))
                    state.parent.alpha = max(score, state.parent.alpha)
                    state.parent.beta = min(score, state.parent.beta)
                    (a1, b1) = state.parent.alpha, state.parent.beta
                    if (a0, b0) == (a1,b1):
                        break
                    state = state.parent
                continue

            if state.childs is None:
                state.childs = []
                color = state.color if state.is_root == True else state.field.invcolor(state.color)
                child_moves = state.field.options(color)
                child_moves = list(sorted(child_moves, key=lambda x : x.score, reverse=True))
                for c_move in child_moves:
                    new_field = copy.deepcopy(state.field)
                    new_field.move(c_move, color)
                    level = (state.level + 1) if state.color != self.color else state.level
                    state.childs.append(State(new_field, level, color, state, c_move))

            if state.child_ix == len(state.childs):
                continue

            c_ix = state.child_ix
            state.child_ix = state.child_ix + 1
            stack.append(state)

            child_state = state.childs[c_ix]

            # alpha-beta cut-off
            if ((child_state.color == self.color and child_state.beta != State.PINF and child_state.beta <= state.alpha) and \
                    child_state.color == self.inv_color and child_state.alpha != State.INF and child_state.alpha >= state.beta) or \
                    child_state.beta == State.PINF:
                        stack.append(child_state)

        return root.movement
