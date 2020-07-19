import json
from loader import *
import numpy as np
from enum import IntEnum
import random
import type
import math
import baseai
modifiers = ["atk", "spatk", "defn", "spdef", "spd"]

class Poke:
  def __init__(self, name):
    self.name = name
    POKE_LIB.loadFromName(self)
    self.curHp = self.hp
    #stat boosts
    self.modifiers = dict(zip(modifiers, [1] * len(modifiers)))
    self.moves = [Move(x) for x in self.moves]
    #this is how i make choosing to switch happen before regular moves
    self.prio = 9

  def stab(self, move):
    return move.type in self.types

  def useMove(self, move, other):
    if self.curHp <= 0:
      return

    hit = random.choices([True, False], [move.acc, 1 - move.acc])[0]
    if not hit:
      return 0

    if move.physical:
      effectiveAtk = self.atk * self.modifiers["atk"]
      effectiveDef = self.defn * self.modifiers["defn"]
    else:
      effectiveAtk = self.spatk * self.modifiers["spatk"]
      effectiveDef = self.spdef * self.modifiers["spdef"]
    
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
    self.team1 = [Poke("Pikachu")]
    self.team2 = [Poke("Pikachu")]
    self.active1 = self.team1[0]
    self.active2 = self.team2[0]
  
  def isGameOver(self):
    return all([mon.curHp <= 0 for mon in self.team1]) or all([mon.curHp <= 0 for mon in self.team2])
  
  def executeAiAction(self, action):
    if isinstance(action, Poke):
      self.active2 = action
      print("AI switched to {0}".format(action.name))
    else:
      if self.active2.curHp <= 0:
        return
      print("AI used {0}".format(action.name))
      damage = self.active2.useMove(action, self.active1)
      print("Player's {0} took {1} damage".format(self.active1.name, damage))

  def executePAction(self, action):
    if isinstance(action, Poke):
      self.active1 = Poke
      print("Player switched to {0}".format(action.name))
    else:
      if self.active1.curHp <= 0:
        return
      print("Player used {0}".format(action.name))
      damage = self.active1.useMove(action, self.active2)
      print("Ai's {0} took {1} damage".format(self.active2.name, damage))
  
  def makeMove(self, pmove):
    aimove = self.ai.chooseAction(self.active2, self.team2, self.active1, self.team1)

    aiprio = aimove.prio * 10000 + self.active2.spd
    pprio = pmove.prio * 10000 + self.active1.spd

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


  def __repr__(self):
    lines = []
    lines.append("Active Player Pokemon: {0} - {1}/{2}".format(self.active1.name, self.active1.curHp, self.active1.hp))
    lines.append("")
    lines.append("AI Player Pokemon: {0} - {1}/{2}".format(self.active2.name, self.active2.curHp, self.active2.hp))


    return "\n".join(lines)