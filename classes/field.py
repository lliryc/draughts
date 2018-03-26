import numpy as np
import copy
from classes.movement import Movement

class Field:
    WHITE = 1
    BLACK = 2
    EMPTY = 0
    BLOCK = 3

    SIZE = 8
    FIGURES = (3 * 8) / 2

    def __init__(self):
        self.desk = np.zeros(shape=(self.SIZE, self.SIZE))
        self.score = {Field.WHITE: 0, Field.BLACK: 0, -1: False}
        self.kingrows = {Field.WHITE: self.SIZE - 1, Field.BLACK: 0}
        self.hash_dict = {}
        # fill whites
        for i in range(0,3):
            for j in range(0,8):
                if (i + j) % 2 == 0:
                    self.desk[i][j] = 1
                else:
                    self.desk[i][j] = 3
        # fill space
        for i in range(3,5):
            for j in range(0,8):
                if (i + j) % 2 == 0:
                    self.desk[i][j] = 0
                else:
                    self.desk[i][j] = 3
        # fill blacks
        for i in range(5,8):
            for j in range(0,8):
                if (i + j) % 2 == 0:
                    self.desk[i][j] = 2
                else:
                    self.desk[i][j] = 3


    def invcolor(self, color):
        if color == self.WHITE:
            return self.BLACK

        if color == self.BLACK:
            return self.WHITE

        return color # by default

    def _move(self, desk, hash_dict, score, movement, color):

        steps = movement.steps
        if len(steps) < 2:
            raise Exception("empty move")
        (x0,y0), *steps = steps
        if desk[x0][y0] % 10 != color :
            raise Exception("illegal move")
        (x,y) = (x0,y0)
        eaten = []

        while len(steps) != 0:
            (x1, y1), *steps = steps

            if x1 < 0 or x1 > self.SIZE or y1 < 0 or y1 > self.SIZE:
                return Exception("illegal move")

            if desk[x1,y1] % 10 == self.BLOCK or (desk[x1,y1] % 10 == color and (x1 != x0 and y1 != y0)):
                raise Exception("illegal move")

            if desk[x1,y1] % 10 == self.invcolor(color) and len(steps) == 0:
                raise Exception("illegal move")

            #if len(eaten) > 0 :
            #    (xe,ye) = eaten[-1]
            #    if (np.abs(xe - x1), np.abs(ye - y1)) != (1, 1):
            #       raise Exception("illegal move")

            if (np.abs(x - x1), np.abs(y - y1)) != (1, 1):
                raise Exception("illegal move")

            if desk[x1,y1] % 10 == self.invcolor(color):
                eaten.append((x1,y1))

            (x,y) = (x1,y1)

        # the moving was correct, apply changes

        for (xe, ye) in eaten:
            desk[xe,ye] = self.EMPTY
        score[color] = score[color] + len(eaten)

        # set target position
        desk[x][y] = desk[x0][y0]
        # clean initial position
        desk[x0][y0] = self.EMPTY

        # check for kings
        if x == self.kingrows[color] and desk[x][y] / 10 < 1:
            desk[x][y] = desk[x][y] + 10

        desk_hash = hash(str(desk))

        if desk_hash in hash_dict:
            if hash_dict[desk_hash] == 2:
                score[-1] = True
            else:
                hash_dict[desk_hash] = self.hash_dict[desk_hash] + 1
        else:
            hash_dict[desk_hash] = 1

        return (x, y)

    def move(self, movement, color):
        return self._move(self.desk, self.hash_dict, self.score, movement, color)

    def _complex_options(self, root_desk, root_hash_dict, score, position, next_moves, color):
        neighbour_moves = next_moves(root_desk, position, color)
        end_moves = []
        end_moves.extend([n_move for n_move in neighbour_moves if n_move.score == 0])
        neighbour_moves = [(n_move, copy.deepcopy(root_desk), copy.deepcopy(root_hash_dict), copy.deepcopy(score)) for n_move in neighbour_moves if n_move.score > 0]
        while len(neighbour_moves) > 0:
            next_n_moves = []
            for n_move, desk, hash_dict, score in neighbour_moves:
                new_desk = copy.deepcopy(desk)
                new_hash_dict = copy.deepcopy(hash_dict)
                new_score = copy.deepcopy(score)
                self._move(new_desk, new_hash_dict, new_score, n_move, color)
                target = n_move.steps[-1]
                child_neighbour_moves = next_moves(new_desk, target, color)
                score_moves = [cn_move for cn_move  in child_neighbour_moves if cn_move.score > 0]
                if len(score_moves) == 0:
                    end_moves.append(n_move)
                else:
                    for score_move in score_moves:
                        next_n_move = copy.deepcopy(n_move)
                        next_n_move.add(score_move)
                        next_n_moves.append((next_n_move, desk, hash_dict, copy.deepcopy(score)))
            neighbour_moves = next_n_moves
        return end_moves


    def options(self, color):
        opts = []
        my_checkers = []
        rows = range(0,self.SIZE)
        if color == self.BLACK:
            rows = reversed(rows)
        for i in rows:
            for j in range(0,self.SIZE):
                if self.desk[i][j] % 10 == color:
                    my_checkers.append((i,j))
        moves = []

        for x,y in my_checkers:
            end_moves = []
            if self.desk[x][y] // 10 == 1:
                end_moves = self._complex_options(self.desk, self.hash_dict, self.score, (x,y), self.neighbour_king_moves, color)
            else:
                end_moves = self._complex_options(self.desk, self.hash_dict, self.score, (x,y), self._neighbour_moves, color)
            moves.extend(end_moves)

        filter_moves = [m for m in moves if m.score > 0]

        if len(filter_moves) > 0:
            return filter_moves

        return moves

    def _diag_moves(self, desk, moves, direction, r, cell, color):
        x,y = cell
        dx,dy = direction
        movement = Movement(cell)
        for i in range(1, r + 1):
            x0, y0 = x + dx*i, y + dy*i
            if desk[x0][y0] % 10 == self.EMPTY:
                if (color == Field.WHITE and x0 == x - 1) or (color == Field.BLACK and x0 == x + 1):
                    break
                movement.steps.append((x0, y0))
                moves.append(copy.deepcopy(movement))
                break
            elif desk[x0][y0] % 10 == self.invcolor(color):
                movement.steps.append((x0,y0))
                movement.score = movement.score + 1
                continue
            else:
                break

    def _neighbour_moves(self, desk, position, color):
        x,y = position
        movements = []
        lower_x = max(x - 2, 0)
        upper_x = min(x + 2, self.SIZE - 1)

        lower_y = max(y - 2, 0)
        upper_y = min(y + 2, self.SIZE - 1)

        for r_max, dir in (min(y - lower_y, x - lower_x), (-1,-1)), \
                          (min(upper_y - y, upper_x - x), ( 1, 1)), \
                          (min(y - lower_y, upper_x - x), ( 1,-1)), \
                          (min(upper_y - y, x - lower_x), (-1, 1)):
            self._diag_moves(desk,movements, dir, r_max, position, color)
        return movements

    def _diag_king_moves(self, desk, moves, direction, r, cell, color):
        tmp_moves = []
        x,y = cell
        dx,dy = direction
        movement = Movement(cell)
        px, py = x,y
        for i in range(1, r + 1):
            x0, y0 = x + dx*i, y + dy*i
            if desk[x0][y0] % 10 == self.EMPTY:
                movement.steps.append((x0, y0))
                tmp_moves.append(copy.deepcopy(movement))
            elif desk[x0][y0] % 10 == self.invcolor(color):
                if desk[px][py] == self.EMPTY or (px == x and py == y):
                    movement.steps.append((x0,y0))
                    movement.score = movement.score + 1
                else:
                    break
            else:
                break
            px,py = x0,y0
        if len(tmp_moves) >0:
            moves.append(tmp_moves[-1])

    def neighbour_king_moves(self, desk, position, color):
        x,y = position
        moves = []
        lower_x = max(x - (self.SIZE - 1), 0)
        upper_x = min(x + (self.SIZE - 1), self.SIZE - 1)

        lower_y = max(y - (self.SIZE - 1), 0)
        upper_y = min(y + (self.SIZE - 1), self.SIZE - 1)

        for r_max, dir in (min(y - lower_y, x - lower_x), (-1,-1)), \
                          (min(upper_y - y, upper_x - x), ( 1, 1)), \
                          (min(y - lower_y, upper_x - x), ( 1,-1)), \
                          (min(upper_y - y, x - lower_x), (-1, 1)):
            self._diag_king_moves(desk, moves, dir, r_max, position, color)
        return moves

    def game_over(self):
        return (self.score[Field.BLACK] == self.FIGURES)\
               or (self.score[Field.WHITE] == self.FIGURES)\
               or self.score[-1] == True

    def blacks_win(self):
        return self.score[Field.BLACK] == self.FIGURES

    def whites_win(self):
        return self.score[Field.WHITE] == self.FIGURES

    def win(self, color):
        return self.score[color] == self.FIGURES

    def display(self):
        for i in reversed(range(0, Field.SIZE)):
            for j in range(0, Field.SIZE):
                bc = self.desk[i][j] % 10
                c = ' ' if bc == 0 else ('*' if bc == 3 else ('w' if bc == 1 else 'b'))
                print(c, end = " ")
            print()
        for k in self.score:
            bc = k
            c = ' ' if bc == 0 else ('*' if bc == 3 else ('w' if bc == 1 else 'b'))
            print("{}:{}".format(c, self.score[k]), end=" ")
        print()
