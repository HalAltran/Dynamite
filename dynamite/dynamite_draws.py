import random


class DynamiteDraws:
    global random

    def __init__(self):
        self.dynamite_count = 0
        self.draws_in_a_row = 0

    def make_move(self, gamestate):
        rounds = gamestate['rounds']

        chosen_move = self.get_random_rps()

        if len(rounds) > 0:
            self.update_draws_in_a_row(rounds[-1])
            if self.use_dynamite():
                chosen_move = 'D'
        self.update_dynamite_count(chosen_move)

        return chosen_move

    def update_dynamite_count(self, chosen_move):
        if chosen_move == 'D':
            self.dynamite_count += 1

    def update_draws_in_a_row(self, last_round):
        if last_round['p1'] == last_round['p2']:
            self.draws_in_a_row += 1
        else:
            self.draws_in_a_row = 0

    def use_dynamite(self):
        if self.dynamite_count < 100:
            if self.draws_in_a_row >= 2:
                return True
        return False

    @staticmethod
    def get_random_rps():
        return random.choice(['R', 'P', 'S'])
