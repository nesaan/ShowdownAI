import json
from loader import *
import numpy as np
from enum import IntEnum
import random
import type
import math
import baseai
from secondaryactions import secondarydict

DEFAULT_MODIFIERS = {
  "atk": 0,
  "spatk":0,
  "defn": 0,
  "spdef": 0,
  "spd": 0
}

class Move:
  def __init__(self, name):
    self.name = name
    MOVE_LIB.loadFromName(self)
    self.secondary = secondarydict[name]

class MoveCache:
  def __init__(self):
    self.moves = {}

  def getMove(self, name):
    if name in self.moves:
      return self.moves[name]
    else:
      self.moves[name] = Move(name)
      return self.moves[name]

moveCache = MoveCache()

class Poke:
  def __init__(self, name):
    self.name = name
    POKE_LIB.loadFromName(self)
    self.curHp = self.hp
    #stat boosts
    self.modifiers = DEFAULT_MODIFIERS.copy()
    self.moves = [moveCache.getMove(x) for x in self.moves]
    #this is how i make choosing to switch happen before regular moves
    self.prio = 9
    self.flinch = False
    self.poison = False
    self.grounded = False

  def stab(self, move):
    return move.type in self.types

  def statboost(self, stat):
    stage = self.modifiers[stat]
    return (max(stage, 0) + 2) / (abs(min(stage, 0)) + 2)

  def useMove(self, move, other):
    if self.curHp <= 0:
      return
    bonusacc = 1.1 if self.ability == "victory star" else 1
    hit = random.choices([True, False], [move.acc * bonusacc, 1 - move.acc*bonusacc])[0]
    if not hit:
      return 0

    if move.physical:
      effectiveAtk = self.atk * self.statboost("atk")
      effectiveDef = other.defn * other.statboost("defn")
    else:
      effectiveAtk = self.spatk * self.statboost("spatk")
      effectiveDef = other.spdef * other.statboost("spdef")

    bpbonus = 2 if move.type == "water" and self.ability == "water bubble" else 1
    bpbonus2 = 1.5 if move.bp <= 60 and self.ability == "technician" else 1

    damage = ((200/5 + 2) * move.bp * bpbonus * bpbonus2 * (effectiveAtk/effectiveDef)/50 + 2)
    targets = 1
    weather = 1
    crit = random.choices([1, 1.5], [100 - 6.25, 6.25])[0]
    randf = random.uniform(0.85, 1)
    stab = 1.5 if self.stab(move) else 1
    eff = type.effective(move.type, other.types)
    #status not implemented
    burn = 1
    #items not implemented
    remainder = 0.5 if move.type == "fire" and other.ability == "water bubble" else 1
    remainder2 = 0 if move.type == "ground" and other.ability == "levitate" and not self.ability == "moldbreaker" and not other.grounded else 1
    
    total = min(math.floor(damage * targets * weather * crit * randf * stab * eff * burn * remainder * remainder2), other.curHp)
    other.curHp -= total
    if other.curHp > 0:
      move.secondary(self, other)

    return total


class Battle:
  def __init__(self, ai):
    self.ai = ai
    self.team1 = [Poke("Alakazam"), Poke("Victini"), Poke("Araquanid"), Poke("Scizor"), Poke("Excadrill"), Poke("Mega-Latios")]
    self.team2 = [Poke("Alakazam"), Poke("Victini"), Poke("Araquanid"), Poke("Scizor"), Poke("Excadrill"), Poke("Mega-Latios")]
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
      if self.active2.curHp <= 0 or self.active2.flinch:
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
      if self.active1.curHp <= 0 or self.active1.flinch:
        return
      print("Player's {0} used {1}".format(self.active1.name, action.name))
      damage = self.active1.useMove(action, self.active2)
      print("Ai's {0} took {1} damage\n".format(self.active2.name, damage))
  
  def makeMove(self, pmove):
    #maybe should check later but i am assuming the ai never makes invalaid moves, but player might because they are either a human or a training ai
    if isinstance(pmove, Poke) and (pmove.curHp <= 0 or pmove == self.active1):
      return
    
    if self.active1.curHp <= 0:
      if isinstance(pmove, Poke):
        if self.active2.curHp <= 0:
          aimove = self.ai.chooseAction(self.active2, self.team2, self.active1, self.team1)
          if isinstance(aimove, Move) or aimove.curHp <= 0:
            raise Exception("Reallyyy bad AI choice, is this guy trained?")
          self.executeAiAction(aimove)
        self.executePAction(pmove)
      return

    aimove = self.ai.chooseAction(self.active2, self.team2, self.active1, self.team1)
    if isinstance(aimove, Poke) and (aimove.curHp <= 0 or aimove == self.active2):
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
    
    # post turn cleanup
    self.active1.flinch = False
    self.active2.flinch = False
    self.active1.grounded = False
    self.active2.grounded = False
    if self.active1.poison and self.active1.ability != "magic guard":
      self.active1.curHp -= min(self.hp, math.floor(self.hp * (1/8)))
    if self.active2.poison and self.active2.ability != "magic guard":
      self.active2.curHp -= min(self.hp, math.floor(self.hp * (1/8)))


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
    for i in range(4):
      lines.append("{0}: {1}".format(i, self.active1.moves[i].name))
    for i in range(6):
      lines.append("{0}: Switch into {1}".format(i+4, self.team1[i].name))


    return "\n".join(lines)