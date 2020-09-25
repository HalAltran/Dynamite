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
        self.match_up_dict = {
              "R": {
                "R": "D",
                "P": "L",
                "S": "W",
                "D": "L",
                "W": "W"
              },
              "P": {
                "R": "W",
                "P": "D",
                "S": "L",
                "D": "L",
                "W": "W"
              },
              "S": {
                "R": "L",
                "P": "W",
                "S": "D",
                "D": "L",
                "W": "W"
              },
              "D": {
                "R": "W",
                "P": "W",
                "S": "W",
                "D": "D",
                "W": "L"
              },
              "W": {
                "R": "L",
                "P": "L",
                "S": "L",
                "D": "W",
                "W": "D"
              }
            }
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
        self.last_strategy_used = None

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

        self.update_strategy_result(rounds[-1])

        self.sort_strategies()

        for strategy in self.strategies:
            if strategy.is_applicable(self, rounds):
                chosen_move = strategy.get_letter(self, rounds)
                self.last_strategy_used = strategy

        if self.last_strategy_used is not None:
            self.last_strategy_used.times_used += 1

        return chosen_move

    def update_strategy_result(self, last_round):
        if self.last_strategy_used is not None:
            if self.get_round_result(last_round) == 'W':
                self.last_strategy_used.wins += 1
            else:
                self.last_strategy_used.losses_or_draws += 1

    def get_round_result(self, round_dict):
        my_move = round_dict['p1']
        opponents_move = round_dict['p2']

        return self.match_up_dict[my_move][opponents_move]

    def sort_strategies(self):
        for strategy in self.strategies:
            strategy.update_success_rate()
        self.strategies.sort(key=lambda entry: entry.success_rate)

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

    def use_water(self):
        if not self.never_use_water:
            return 'W'
        return self.get_random_rps()

    @staticmethod
    def get_random_rps():
        return random.choice(['R', 'P', 'S'])

    class Strategy:

        def __init__(self):
            self.success_rate = 0
            self.use_strategy = True
            self.wins = 0
            self.losses_or_draws = 0
            self.draws = 0
            self.times_used = 0

        def is_applicable(self, mario_and_luigi, rounds):
            if self.use_strategy:
                return self.is_applicable_abstract(mario_and_luigi, rounds)
            return False

        def update_success_rate(self):
            if self.times_used < 5 and self.success_rate <= 60:
                self.success_rate = 40 + random.randint(0, 20)
            else:
                self.success_rate = int((float(self.wins) / float(self.times_used)) * 100)

        @abstractmethod
        def is_applicable_abstract(self, mario_and_luigi, rounds):
            pass

        @abstractmethod
        def get_letter(self, mario_and_luigi, rounds):
            pass

    class DynamiteDraws(Strategy):

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            if mario_and_luigi.dynamite_count == 100:
                self.use_strategy = False
                return False
            if mario_and_luigi.draws_in_a_row >= 2:
                return True

        def get_letter(self, mario_and_luigi, rounds):
            return 'D'

    class BeatRepeatedMove(Strategy):

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

    class Opponent:

        def __init__(self):
            self.dynamite_count = 0
            self.last_ten_moves = []
