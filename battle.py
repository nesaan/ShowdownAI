import json
from loader import *
import numpy as np
from enum import IntEnum
import random
import type
import math
import baseai

DEFAULT_MODIFIERS = {
  "atk": 0,
  "spatk":0,
  "defn": 0,
  "spdef": 0,
  "spd": 0
}

class Poke:
  def __init__(self, name):
    self.name = name
    POKE_LIB.loadFromName(self)
    self.curHp = self.hp
    #stat boosts
    self.modifiers = DEFAULT_MODIFIERS.copy()
    self.moves = [Move(x) for x in self.moves]
    #this is how i make choosing to switch happen before regular moves
    self.prio = 9

  def stab(self, move):
    return move.type in self.types

  def statboost(self, stat):
    stage = self.modifiers[stat]
    return (max(stage, 0) + 2) / (abs(min(stage, 0)) + 2)

  def useMove(self, move, other):
    if self.curHp <= 0:
      return

    hit = random.choices([True, False], [move.acc, 1 - move.acc])[0]
    if not hit:
      return 0

    if move.physical:
      effectiveAtk = self.atk * self.statboost("atk")
      effectiveDef = other.defn * other.statboost("defn")
    else:
      effectiveAtk = self.spatk * self.statboost("spatk")
      effectiveDef = other.spdef * other.statboost("spdef")
    
    damage = ((200/5 + 2) * move.bp * (effectiveAtk/effectiveDef)/50 + 2)
    targets = 1
    weather = 1
    crit = random.choices([1, 1.5], [100 - 6.25, 6.25])[0]
    randf = random.uniform(0.85, 1)
    stab = 1.5 if self.stab(move) else 1
    eff = type.effective(move.type, other.types)
    #status not implemented
    burn = 1
    #items not implemented
    remainder = 1

    
    total = min(math.floor(damage * targets * weather * crit * randf * stab * eff * burn * remainder), other.curHp)
    if total > 0:
      total = max(1, total)
    other.curHp -= total
    return total


class Move:
  def __init__(self, name):
    self.name = name
    MOVE_LIB.loadFromName(self)


class Battle:
  def __init__(self, ai):
    self.ai = ai
    self.team1 = [Poke("Alakazam")]
    self.team2 = [Poke("Alakazam")]
    self.active1 = self.team1[0]
    self.active2 = self.team2[0]
  
  def isGameOver(self):
    return all(mon.curHp <= 0 for mon in self.team1) or all(mon.curHp <= 0 for mon in self.team2)
  
  def executeAiAction(self, action):
    if isinstance(action, Poke):
      self.active2 = action
      action.modifiers = DEFAULT_MODIFIERS.copy()
      print("AI switched to {0}\n".format(action.name))
    else:
      if self.active2.curHp <= 0:
        return
      print("AI's {0} used {1}".format(self.active2.name, action.name))
      damage = self.active2.useMove(action, self.active1)
      print("Player's {0} took {1} damage\n".format(self.active1.name, damage))

  def executePAction(self, action):
    if isinstance(action, Poke):
      self.active1 = action
      action.modifiers = DEFAULT_MODIFIERS.copy()
      print("Player switched to {0}\n".format(action.name))
    else:
      if self.active1.curHp <= 0:
        return
      print("Player's {0} used {1}".format(self.active1.name, action.name))
      damage = self.active1.useMove(action, self.active2)
      print("Ai's {0} took {1} damage\n".format(self.active2.name, damage))
  
  def makeMove(self, pmove):
    #maybe should check later but i am assuming the ai never makes invalaid moves, but player might because they are either a human or a training ai
    if isinstance(pmove, Poke) and pmove.curHp <= 0:
      return
    
    if self.active1.curHp <= 0:
      if isinstance(pmove, Poke):
        if self.active2.curHp <= 0:
          aimove = self.ai.chooseAction(self.active2, self.team2, self.active1, self.team1)
          if isinstance(aimove, Move):
            raise Exception("Reallyyy bad AI choice, is this guy trained?")
          self.executeAiAction(aimove)
        self.executePAction(pmove)
      return

    aimove = self.ai.chooseAction(self.active2, self.team2, self.active1, self.team1)
    if isinstance(aimove, Poke) and aimove.curHp <= 0:
      raise Exception("Reallyy bad AI choice, is this guy trained?")

    aiprio = aimove.prio * 10000 + self.active2.spd * self.active2.statboost("spd")
    pprio = pmove.prio * 10000 + self.active1.spd * self.active1.statboost("spd")

    #I'm kind of tired, there is def a less dumb way to do this
    if aiprio > pprio:
      self.executeAiAction(aimove)
      self.executePAction(pmove)
    elif pprio > aiprio:
      self.executePAction(pmove)
      self.executeAiAction(aimove)
    else:
      aifirst = bool(random.getrandbits(1))
      if aifirst:
        self.executeAiAction(aimove)
        self.executePAction(pmove)
      else:
        self.executePAction(pmove)
        self.executeAiAction(aimove)
    
    if not self.isGameOver():
      #so when ai's mon is dead, it can choose a new mon, unless both are dead, in which case it has to be done on a simutaneous turn
      while self.active2.curHp <= 0 and self.active1.curHp >= 0:
        aimove = self.ai.chooseAction(self.active2, self.team2, self.active1, self.team1)
        if not isinstance(aimove, Poke):
          raise Exception("Really bad AI choice, is this guy trained?")
        self.executeAiAction(aimove)



  def __repr__(self):
    lines = []
    lines.append("Active Player Pokemon: {0} - {1}/{2}".format(self.active1.name, self.active1.curHp, self.active1.hp))
    lines.append("")
    lines.append("AI Player Pokemon: {0} - {1}/{2}".format(self.active2.name, self.active2.curHp, self.active2.hp))
    lines.append("")
    lines.append("")

    return "\n".join(lines)