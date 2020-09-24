import random


class RandomMoves:

    def __init__(self):
        self.move = 'P'

    def make_move(self, gamestate):
        return self.get_random_rps()

    @staticmethod
    def get_random_rps():
        return random.choice(['R', 'P', 'S'])
