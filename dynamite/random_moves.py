import random


class RandomMoves:
    global random

    def __init__(self):
        self.dynamite_count = 0
        self.move_list = ['R', 'P', 'S', 'D']

    def make_move(self, gamestate):
        move = self.get_random_rps()
        if move == 'D':
            self.dynamite_count += 1
            if self.dynamite_count == 100:
                self.move_list.remove('D')
        return move

    def get_random_rps(self):
        return random.choice(self.move_list)
