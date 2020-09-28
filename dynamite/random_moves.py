import random


class RandomMoves:
    global random

    def __init__(self):
        self.dynamite_count = 0
        self.move_list = ['R', 'P', 'S', 'D']
        self.dynamite_count_down = 7

    def make_move(self, gamestate):
        move = self.get_random_rps()
        # if self.dynamite_count_down == 0:
        #     move = 'D'
        #     self.dynamite_count_down = 7
        # else:
        #     self.dynamite_count_down -= 1

        if move == 'D':
            self.dynamite_count += 1
            if self.dynamite_count == 100:
                # move = self.get_random_rps()
                self.move_list.remove('D')
        return move

    def get_random_rps(self):
        return random.choice(self.move_list)
