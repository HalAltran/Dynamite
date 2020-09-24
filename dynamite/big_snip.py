import random

from copy import deepcopy


MOVE_COUNT_MAP = {'R': 0, 'P': 0, 'S': 0, 'D': 0, 'W': 0}


class BigSnip:

    def __init__(self):
        self.move = 'P'
        self.round_count = 0
        self.opponents_move_counts = deepcopy(MOVE_COUNT_MAP)
        self.opponents_same_move_in_a_row = {}
        self.opponents_last_ten_moves = deepcopy(MOVE_COUNT_MAP)
        self.dynamite_count = 0
        self.dynamites_in_a_row_count = 0

    def make_move(self, gamestate):
        rounds = gamestate['rounds']

        chosen_move = self.get_random_rps()

        if len(rounds) > 0:
            self.update_opponents_moves(rounds)

            if next(iter(self.opponents_same_move_in_a_row.values())) > 2:
                chosen_move = self.move_that_beats_opponents_last_move(rounds)

            if self.use_dynamite():
                chosen_move = 'D'

        self.round_count += 1
        return chosen_move

    def update_opponents_moves(self, rounds):
        last_move = rounds[-1]['p2']

        current_count = 1
        if last_move in self.opponents_move_counts:
            current_count = self.opponents_move_counts[last_move] + 1
        self.opponents_move_counts[last_move] = current_count
        if last_move in self.opponents_same_move_in_a_row:
            self.opponents_same_move_in_a_row[last_move] += 1
        else:
            self.opponents_same_move_in_a_row = {last_move: 1}

        self.opponents_last_ten_moves = deepcopy(MOVE_COUNT_MAP)
        reverse_count = len(rounds)
        if reverse_count > 10:
            reverse_count = 10
        count = 0
        for move in reversed(rounds):
            self.opponents_last_ten_moves[move['p2']] += 1
            count += 1
            if count == reverse_count:
                break

    def move_that_beats_opponents_last_move(self, rounds):
        opponents_last_move = rounds[-1]['p2']
        if opponents_last_move == 'R':
            return 'P'
        elif opponents_last_move == 'P':
            return 'S'
        elif opponents_last_move == 'S':
            return 'R'
        elif opponents_last_move == 'D':
            return 'W'
        return self.get_random_rps()

    def update_opponents_last_ten_moves(self):
        pass

    def use_dynamite(self):
        if self.opponents_last_ten_moves['W'] == 0 and self.dynamites_in_a_row_count < 2 and self.dynamite_count < 100:
            self.dynamite_count += 1
            self.dynamites_in_a_row_count += 1
            return True
        self.dynamites_in_a_row_count = 0
        return False

    @staticmethod
    def get_random_rps():
        return random.choice(['R', 'P', 'S'])
