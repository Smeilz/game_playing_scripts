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

from games import TicTacToe
from gameagent import QLambdaAfterstateAgent

def demo_game_stats(agent):
    results = [agent.demo_game() for i in range(100000)]
    game_stats = {k: results.count(k)/1000 for k in ['X', 'O', '-']}
    print("    percentage results: {}".format(game_stats))

if __name__ == '__main__':
    agent = QLambdaAfterstateAgent(TicTacToe, epsilon = 0.1, alpha = 0.5, lam=0.8)
    print("Before learning:")
    demo_game_stats(agent)

    agent.learn_game(250)
    print("After 250 learning games:")
    demo_game_stats(agent)

    agent.learn_game(250)
    print("After 500 learning games:")
    demo_game_stats(agent)

    agent.learn_game(250)
    print("After 750 learning games:")
    demo_game_stats(agent)

    agent.learn_game(250)
    print("After 1000 learning games:")
    demo_game_stats(agent)

    agent.learn_game(4000)
    print("After 5000 learning games:")
    demo_game_stats(agent)

    # agent.round_V()
    agent.save_v_table()
