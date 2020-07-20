import numpy as np
import gym
from gym import spaces
from battle import *

minaspace = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6]
maxaspace = [6, 6, 251, 404, 340, 323, 362, 301, 251, 404, 340, 323, 362, 301, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]


#edit for multiple ais
class ShowdownGym(gym.Env):
  metadata = {'render.modes': ['console']}

  def __init__(self, ai):
    super(ShowdownGym, self).__init__()
    n_actions = 10
    self.action_space = spaces.Discrete(n_actions)
    self.observation_space = spaces.Box( np.array(minaspace), np.array(maxaspace), dtype=np.int)
    self.ai = ai
    self.battle = Battle(ai)

  def reset(self):
    self.battle = Battle(self.ai)
    return np.array(self.battle.observe())

  def step(self, action):
    if action < 4:
      action_object = self.battle.active1.moves[action]
    else:
      action_object = self.battle.team1[action - 4]
    valid = self.battle.makeMove(action_object)  
    done = bool(self.battle.isGameOver())
    
    reward = self.battle.reward(valid)

    # Optionally we can pass additional info, we are not using that for now
    info = {}

    return np.array(self.battle.observe()), reward, done, info

  def render(self, mode='console'):
    if mode != 'console':
      raise NotImplementedError()
    print(self.battle)

  def close(self):
    pass