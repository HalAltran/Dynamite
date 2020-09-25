import random
import copy

from copy import deepcopy
from abc import abstractmethod


class MarioAndLuigi:
    global random
    global copy
    global deepcopy
    global abstractmethod

    def __init__(self):
        self.move_count_map = {'R': 0, 'P': 0, 'S': 0, 'D': 0, 'W': 0}
        self.move = 'P'
        self.round_count = 0
        self.opponents_move_counts = deepcopy(self.move_count_map)
        self.opponents_same_move_in_a_row = {}
        self.opponents_last_ten_moves = deepcopy(self.move_count_map)
        self.dynamite_count = 0
        self.dynamites_in_a_row_count = 0
        self.opponents_dynamite_count = 0
        self.never_use_water = False
        self.draws_in_a_row = 0
        self.strategies = [self.DynamiteDraws(), self.BeatRepeatedMove()]
        # self.strategies.append(self.DynamiteDraws())

    def make_move(self, gamestate):
        rounds = gamestate['rounds']

        chosen_move = self.get_random_rps()

        if len(rounds) > 0:
            chosen_move = self.choose_move(rounds)
        self.update_moves_used(chosen_move)

        self.round_count += 1
        return chosen_move

    def choose_move(self, rounds):
        self.update_draws_in_a_row(rounds[-1])
        chosen_move = self.get_random_rps()
        self.update_opponents_moves(rounds)

        # if self.use_dynamite():
        #     chosen_move = 'D'

        self.strategies.sort(key=lambda entry: entry.priority)

        for strategy in self.strategies:
            if strategy.is_applicable(self, rounds):
                chosen_move = strategy.get_letter(self, rounds)

        return chosen_move

    def update_moves_used(self, chosen_move):
        if chosen_move == 'D':
            self.dynamite_count += 1
            self.dynamites_in_a_row_count += 1
        else:
            self.dynamites_in_a_row_count = 0

    def update_draws_in_a_row(self, last_round):
        if last_round['p1'] == last_round['p2']:
            self.draws_in_a_row += 1
        else:
            self.draws_in_a_row = 0

    def update_opponents_moves(self, rounds):
        last_move = rounds[-1]['p2']

        current_count = 1
        if last_move == 'D':
            self.opponents_dynamite_count += 1
            if self.opponents_dynamite_count == 100:
                self.never_use_water = True
        if last_move in self.opponents_move_counts:
            current_count = self.opponents_move_counts[last_move] + 1
        self.opponents_move_counts[last_move] = current_count
        if last_move in self.opponents_same_move_in_a_row:
            self.opponents_same_move_in_a_row[last_move] += 1
        else:
            self.opponents_same_move_in_a_row = {last_move: 1}

        self.opponents_last_ten_moves = deepcopy(self.move_count_map)
        reverse_count = len(rounds)
        if reverse_count > 10:
            reverse_count = 10
        count = 0
        for move in reversed(rounds):
            self.opponents_last_ten_moves[move['p2']] += 1
            count += 1
            if count == reverse_count:
                break

    # def move_that_beats_opponents_last_move(self, rounds):
    #     opponents_last_move = rounds[-1]['p2']
    #     if opponents_last_move == 'R':
    #         return 'P'
    #     elif opponents_last_move == 'P':
    #         return 'S'
    #     elif opponents_last_move == 'S':
    #         return 'R'
    #     elif opponents_last_move == 'D':
    #         return self.use_water()
    #     return self.get_random_rps()

    def use_water(self):
        if not self.never_use_water:
            return 'W'
        return self.get_random_rps()

    def update_opponents_last_ten_moves(self):
        pass

    def use_dynamite(self):
        if self.dynamite_count < 100:
            # if self.opponents_last_ten_moves['W'] == 0 and self.dynamites_in_a_row_count < 2:
            #     return True
            if self.draws_in_a_row >= 2:
                return True
        return False

    @staticmethod
    def get_random_rps():
        return random.choice(['R', 'P', 'S'])

    class Strategy:

        def __init__(self, priority):
            self.priority = priority
            self.success_rate = 0
            self.use_strategy = True
            self.success_count = 0
            self.fail_count = 0

        def is_applicable(self, mario_and_luigi, rounds):
            if self.use_strategy:
                return self.is_applicable_abstract(mario_and_luigi, rounds)
            return False

        @abstractmethod
        def is_applicable_abstract(self, mario_and_luigi, rounds):
            pass

        @abstractmethod
        def get_letter(self, mario_and_luigi, rounds):
            pass

    class DynamiteDraws(Strategy):

        def __init__(self):
            super().__init__(3)

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            if mario_and_luigi.dynamite_count == 100:
                self.use_strategy = False
                return False
            if mario_and_luigi.draws_in_a_row >= 2:
                return True

        def get_letter(self, mario_and_luigi, rounds):
            return 'D'

    class BeatRepeatedMove(Strategy):

        def __init__(self):
            super().__init__(8)

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            return next(iter(mario_and_luigi.opponents_same_move_in_a_row.values())) >= 2

        def get_letter(self, mario_and_luigi, rounds):
            return self.move_that_beats_opponents_last_move(mario_and_luigi, rounds)

        @staticmethod
        def move_that_beats_opponents_last_move(mario_and_luigi, rounds):
            opponents_last_move = rounds[-1]['p2']
            if opponents_last_move == 'R':
                return 'P'
            elif opponents_last_move == 'P':
                return 'S'
            elif opponents_last_move == 'S':
                return 'R'
            elif opponents_last_move == 'D':
                return mario_and_luigi.use_water()
            return mario_and_luigi.get_random_rps()
