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
        self.match_up_dict = self.get_match_up_dict()
        self.move_count_map = {'R': 0, 'P': 0, 'S': 0, 'D': 0, 'W': 0}

        self.opponent = self.Opponent(self)

        self.round_count = 0
        self.dynamite_count = 0
        self.dynamites_in_a_row_count = 0

        self.draw_count = 0
        self.draw_multiplier = 0
        self.draws_won = 0
        self.draws_lost = 0
        self.draw_win_rate = 50

        self.last_result = None

        self.can_use_water = True

        beat_repeated_five = self.BeatRepeatedMove(5)
        beat_repeated_five.success_rate = 100

        beat_repeated_eleven = self.BeatRepeatedMove(11)
        beat_repeated_five.success_rate = 100

        self.strategies = [self.RandomRPS(), self.DynamiteDraws(2), self.DynamiteDraws(3), self.BeatRepeatedMove(2),
                           self.WaterDraws(2), self.WaterDraws(3), self.PredictDynamiteAtInterval(), beat_repeated_five,
                           beat_repeated_eleven, self.PatternTrick(2), self.PatternTrick(3)]

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
        self.update_draw_multiplier(rounds[-1])
        chosen_move = self.get_random_rps()

        self.opponent.update_moves(rounds)

        self.update_strategy_result(rounds[-1])
        self.add_new_strategies_if_appropriate()

        self.update_strategy_success_rate_and_sort()

        for strategy in self.strategies:
            if strategy.is_applicable(self, rounds):
                chosen_move = strategy.get_letter(self, rounds)
                self.last_strategy_used = strategy

        if self.last_strategy_used is not None:
            self.last_strategy_used.times_used += 1

        return chosen_move

    def update_strategy_result(self, last_round):
        if self.last_strategy_used is not None:
            latest_result = self.get_round_result(last_round)
            self.update_draw_win_rate(latest_result)

            self.last_result = latest_result
            if self.last_result == 'W':
                # self.last_strategy_used.wins += self.draw_multiplier
                self.last_strategy_used.wins += 1
            elif self.last_result == 'L':
                # self.last_strategy_used.losses += self.draw_multiplier
                self.last_strategy_used.losses += 1
            else:
                self.last_strategy_used.draws += 1
                self.draw_count += 1

    def get_round_result(self, round_dict):
        my_move = round_dict['p1']
        opponents_move = round_dict['p2']

        return self.match_up_dict[my_move][opponents_move]

    def update_draw_win_rate(self, latest_result):
        if self.draw_count > 0 and self.last_result == 'D':
            if latest_result == 'W':
                self.draws_won += 1
            elif latest_result == 'L':
                self.draws_lost += 1
            if self.draws_won > 0 or self.draws_lost > 0:
                self.draw_win_rate = int(float(self.draws_won) / float(self.draws_won + self.draws_lost) * 100)

    def update_strategy_success_rate_and_sort(self):
        for strategy in self.strategies:
            strategy.update_success_rate(self.draw_win_rate)
        self.strategies.sort(key=lambda entry: entry.success_rate)

    def update_moves_used(self, chosen_move):
        if chosen_move == 'D':
            self.dynamite_count += 1
            self.dynamites_in_a_row_count += 1
        else:
            self.dynamites_in_a_row_count = 0

    def update_draw_multiplier(self, last_round):
        if last_round['p1'] == last_round['p2']:
            self.draw_multiplier += 1
        else:
            self.draw_multiplier = 1

    def add_new_strategies_if_appropriate(self):
        if self.dynamite_count < 60 and self.round_count > 1000 and\
                not any(isinstance(strategy, self.DynamitePrimes) for strategy in self.strategies):
            self.strategies.append(self.DynamitePrimes())

    @staticmethod
    def get_random_rps():
        return random.choice(['R', 'P', 'S'])

    class Strategy:

        def __init__(self):
            self.success_rate = 0
            self.use_strategy = True
            self.wins = 0
            self.losses = 0
            self.draws = 0
            self.times_used = 0

        def is_applicable(self, mario_and_luigi, rounds):
            if self.use_strategy:
                return self.is_applicable_abstract(mario_and_luigi, rounds)
            return False

        def update_success_rate(self, overall_draw_win_rate):
            if self.times_used < 4 and self.success_rate <= 60:
                self.success_rate = 51 + random.randint(0, 9)
            elif self.times_used > 0:
                win_rate = (float(self.wins) / float(self.times_used)) * 100
                draw_win_rate = float(overall_draw_win_rate * self.draws) / float(self.times_used)
                self.success_rate = int(win_rate + draw_win_rate)

        @abstractmethod
        def is_applicable_abstract(self, mario_and_luigi, rounds):
            pass

        @abstractmethod
        def get_letter(self, mario_and_luigi, rounds):
            pass

    class RandomRPS(Strategy):

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            return True

        def get_letter(self, mario_and_luigi, rounds):
            return mario_and_luigi.get_random_rps()

    class DynamiteDraws(Strategy):

        def __init__(self, consecutive_draws):
            super().__init__()
            self.consecutive_draws = consecutive_draws

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            if mario_and_luigi.dynamite_count == 100:
                self.use_strategy = False
                return False
            if mario_and_luigi.draw_multiplier > self.consecutive_draws:
                return True
            return False

        def get_letter(self, mario_and_luigi, rounds):
            return 'D'

    class BeatRepeatedMove(Strategy):

        def __init__(self, number_of_repetitions):
            super().__init__()
            self.number_of_repetitions = number_of_repetitions

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            return next(iter(mario_and_luigi.opponent.same_move_in_a_row.values())) >= self.number_of_repetitions and\
                   self.can_use_water_if_opponents_last_move_was_dynamite(mario_and_luigi, rounds[-1]['p2'])

        def get_letter(self, mario_and_luigi, rounds):
            return self.move_that_beats_opponents_last_move(mario_and_luigi, rounds)

        @staticmethod
        def can_use_water_if_opponents_last_move_was_dynamite(mario_and_luigi, opponents_last_move):
            return opponents_last_move != 'D' or mario_and_luigi.can_use_water

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
                return 'W'
            return mario_and_luigi.get_random_rps()

    class DynamitePrimes(Strategy):

        def __init__(self):
            super().__init__()
            self.primes = self.get_primes()

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            return mario_and_luigi.dynamite_count < 100 and mario_and_luigi.round_count in self.primes

        def get_letter(self, mario_and_luigi, rounds):
            return 'D'

        @staticmethod
        def get_primes():
            primes = {2}
            for i in range(2, 2500):
                prime_so_far = True
                for prime in primes:
                    if i % prime == 0:
                        prime_so_far = False
                if prime_so_far:
                    primes.add(i)
            return primes

    class PatternTrick(Strategy):

        def __init__(self, number_of_repetitions):
            super().__init__()
            self.number_of_repetitions = number_of_repetitions

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            return len(rounds) >= self.number_of_repetitions and self.last_n_moves_repeated(rounds) and \
                   self.last_move_rps(rounds[-1]['p1'])

        def get_letter(self, mario_and_luigi, rounds):
            return self.lose_to_my_last_move(rounds)

        def last_n_moves_repeated(self, rounds):
            last_move = rounds[-1]['p1']
            for n in range(1, self.number_of_repetitions + 1):
                n_last_move = rounds[-n]['p1']
                if n_last_move == last_move:
                    last_move = n_last_move
                else:
                    return False
            return True

        @staticmethod
        def last_move_rps(last_move):
            return last_move in ['R', 'P', 'S']

        @staticmethod
        def lose_to_my_last_move(rounds):
            last_move = rounds[-1]['p1']
            if last_move == 'R':
                return 'S'
            elif last_move == 'P':
                return 'R'
            return 'P'

    class PredictPattern(Strategy):
        pass

    class PredictDynamiteAtInterval(Strategy):

        def __init__(self):
            super().__init__()
            self.interval_to_wait = None

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            opponents_last_four_dynamites = mario_and_luigi.opponent.last_four_dynamites
            if not mario_and_luigi.can_use_water or len(opponents_last_four_dynamites) < 4:
                return False

            if self.interval_to_wait is not None:
                if self.interval_to_wait == 0:
                    self.interval_to_wait = None
                    return True
                else:
                    self.interval_to_wait -= 1
                    return False

            last_interval = opponents_last_four_dynamites[1] - opponents_last_four_dynamites[0]
            last_round_dynamited = opponents_last_four_dynamites[1]
            for round_dynamited in opponents_last_four_dynamites[2:4]:
                interval = round_dynamited - last_round_dynamited
                if interval == last_interval:
                    last_interval = interval
                    last_round_dynamited = round_dynamited
                else:
                    return False
            self.interval_to_wait = last_interval - 2
            return False

        def get_letter(self, mario_and_luigi, rounds):
            return 'W'

    class WaterDraws(Strategy):

        def __init__(self, consecutive_draws):
            super().__init__()
            self.consecutive_draws = consecutive_draws

        def is_applicable_abstract(self, mario_and_luigi, rounds):
            if mario_and_luigi.opponent.dynamite_count == 100:
                self.use_strategy = False
                return False
            if mario_and_luigi.draw_multiplier > self.consecutive_draws:
                return True

        def get_letter(self, mario_and_luigi, rounds):
            return 'W'

    class Opponent:

        def __init__(self, mario_and_luigi):
            self.mario_and_luigi = mario_and_luigi
            self.dynamite_count = 0
            self.move_counts = deepcopy(self.mario_and_luigi.move_count_map)
            self.last_ten_moves = []
            self.same_move_in_a_row = {}
            self.last_four_dynamites = []

        def update_moves(self, rounds):
            last_move = rounds[-1]['p2']

            current_count = 1
            if last_move == 'D':
                self.dynamite_count += 1
                if self.dynamite_count == 100:
                    self.mario_and_luigi.can_use_water = False
                self.update_last_four_dynamites()
            if last_move in self.move_counts:
                current_count = self.move_counts[last_move] + 1
            self.move_counts[last_move] = current_count
            if last_move in self.same_move_in_a_row:
                self.same_move_in_a_row[last_move] += 1
            else:
                self.same_move_in_a_row = {last_move: 1}

            self.update_last_ten_moves(last_move)

        def update_last_four_dynamites(self):
            if len(self.last_four_dynamites) >= 4:
                self.last_four_dynamites.pop(0)
            self.last_four_dynamites.append(self.mario_and_luigi.round_count)

        def update_last_ten_moves(self, last_move):
            if len(self.last_ten_moves) >= 10:
                self.last_ten_moves.pop(0)
            self.last_ten_moves.append(last_move)

    @staticmethod
    def get_match_up_dict():
        return {
              "R": {"R": "D", "P": "L", "S": "W", "D": "L", "W": "W"},
              "P": {"R": "W", "P": "D", "S": "L", "D": "L", "W": "W"},
              "S": {"R": "L", "P": "W", "S": "D", "D": "L", "W": "W"},
              "D": {"R": "W", "P": "W", "S": "W", "D": "D", "W": "L"},
              "W": {"R": "L", "P": "L", "S": "L", "D": "W", "W": "D"}
        }
