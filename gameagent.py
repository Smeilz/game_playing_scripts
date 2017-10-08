'''
   Copyright 2017 Neil Slater

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import numpy as np
import csv
import random
from itertools import groupby

class AfterStateBase():
    def __init__(self, game_class, epsilon=0.1, alpha=1.0, value_player='X'):
        self.V = dict()
        self.NewGame = game_class
        self.epsilon = epsilon
        self.alpha = alpha
        self.value_player = value_player

    def state_value(self, game_state):
        return self.V.get(game_state, 0.0)

    def learn_game(self, num_episodes=1000):
        for episode in range(num_episodes):
            self.learn_from_episode()

    def play_select_move(self, game):
        allowed_state_values = self._state_values( game.allowed_moves() )
        if game.player == self.value_player:
            return self._argmax_V(allowed_state_values)
        else:
            return self._argmin_V(allowed_state_values)

    def demo_game(self, verbose=False):
        game = self.NewGame()
        while game.playable():
            if verbose:
                game.display()
            move = self.play_select_move(game)
            game.make_move(move)
        if verbose:
            game.display()
        if game.winner:
            if verbose:
                print("\n{} is the winner!".format(game.winner))
            return game.winner
        else:
            if verbose:
                print("\nIt's a draw!")
            return '-'

    def interactive_game(self, agent_player='X'):
        game = self.NewGame()
        while game.playable():
            game.display()
            if game.player == agent_player:
                move = self.play_select_move(game)
                game.make_move(move)
            else:
                move = game.request_human_move()
                game.make_move(move)
        game.display()

        if game.winner:
            print("\n{} is the winner!".format(game.winner))
            return game.winner
        print("\nIt's a draw!")
        return '-'

    def round_V(self):
        # After training, this makes action selection random from equally-good choices
        for k in self.V.keys():
            self.V[k] = round(self.V[k],1)

    def save_v_table(self, filename='state_values.csv'):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['State', 'Value'])
            all_states = list(self.V.keys())
            all_states.sort()
            for state in all_states:
                writer.writerow([state, self.V[state]])

    def _state_values(self, game_states):
        return dict((state, self.state_value(state)) for state in game_states)

    def _argmax_V(self, state_values):
        max_V = max(state_values.values())
        chosen_state = random.choice([state for state, v in state_values.items() if v == max_V])
        return chosen_state

    def _argmin_V(self, state_values):
        min_V = min(state_values.values())
        chosen_state = random.choice([state for state, v in state_values.items() if v == min_V])
        return chosen_state

    def _random_V(self, state_values):
        return random.choice(list(state_values.keys()))

    def _reward(self, game):
        if game.winner == self.value_player:
            return 1.0
        elif game.winner:
            return -1.0
        else:
            return 0.0

class QAfterstateAgent(AfterStateBase):
    '''
    QAfterstateAgent can in theory learn any zero-sum 2 player game where the only reward is +1 for
    a win, 0 for a draw and -1 for a loss. In practice it will be too slow for complex games.

    The game_class parameter must have the following behaviour:

      * No constructor params, the game should initialise ready to start play

      * state property, which should be suitable for use as a dict key

      * player property, which should have two possible values

      * winner property, which should be none, or have same two possible values as player

      * playable() method returning True when play may continue

      * allowed_moves() method which returns list of valid next moves

      * make_move(new_state) method which checks and applies requested move

      * request_human_move() method which allows human to make move for current player

      * display() method which shows current game state
    '''
    def learn_from_episode(self):
        game = self.NewGame()
        while game.playable():
            self.learn_from_move(game)
        self.V[game.state] = self._reward(game)

    def learn_from_move(self, game):
        current_state = game.state
        best_next_move, selected_next_move = self.learn_select_move(game)
        r = self._reward(game)

        current_state_value = self.state_value(current_state)
        best_move_value = self.state_value(best_next_move)
        td_target = r + best_move_value
        self.V[current_state] = current_state_value + self.alpha * (td_target - current_state_value)

        game.make_move(selected_next_move)

    def learn_select_move(self, game):
        allowed_state_values = self._state_values( game.allowed_moves() )
        if game.player == self.value_player:
            best_move = self._argmax_V(allowed_state_values)
        else:
            best_move = self._argmin_V(allowed_state_values)

        selected_move = best_move
        if random.random() < self.epsilon:
            selected_move = self._random_V(allowed_state_values)

        return (best_move, selected_move)

