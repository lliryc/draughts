from classes.minmax_player import MinMaxPlayer
from classes.monte_carlo_player import MonteCarloPlayer
from classes.field import Field

if __name__ == "__main__":

    game_field = Field()

    player1 = MonteCarloPlayer(Field.WHITE, game_field, 30)

    player2 = MonteCarloPlayer(Field.BLACK, game_field, 40)
    #player2 = MinMaxPlayer(Field.BLACK, game_field, 3)
    print("start of game")
    game_field.display()
    while True:
        player1.move()
        print("Player 1's turn")
        game_field.display()


        if game_field.game_over():
            if game_field.whites_win():
                print("Player 1 wins")
            else:
                print("Draw")
            break

        player2.move()
        print("Player 2's turn")
        game_field.display()

        if game_field.game_over():
            if game_field.blacks_win():
                print("Player 2 wins")
            else:
                print("Draw")
            break

