import random
import math

def flip(prob):
  return random.choices([1, 0], [prob, 1-prob])[0]

def earthquake(attk, defn):
  pass

def psychic(attk, defn):
  defn.modifiers["spdef"] -= flip(1)

def shadowball(attk, defn):
  defn.modifiers["spdef"] -= flip(0.2)

def focusblast(attk, defn):
  defn.modifiers["spdef"] -= flip(0.1)

def dazzlinggleam(attk, defn):
  pass

def vcreate(attk, defn):
  attk.modifiers["defn"] -= 1
  attk.modifiers["spdef"] -= 1
  attk.modifiers["spd"] -= 1

def boltstrike(attk, defn):
  #someone implement paralysis if they want
  pass

def finalgambit(attk, defn):
  defn.curHp -= min(attk.curHp, defn.curHp)
  attk.curHp = 0

def zenheadbutt(attk, defn):
  if flip(0.2):
    defn.flinch = True

def liquidation(attk, defn):
  if flip(0.2):
    defn.modifiers["defn"] -= 1

def crunch(attk, defn):
  if flip(0.2):
    defn.modifiers["defn"] -= 1

def poisonjab(attk, defn):
  if flip(0.3):
    defn.poison = True

def xscissor(attk, defn):
  pass

def bugbite(attk, defn):
  pass

def bulletpunch(attk, defn):
  pass

def agility(attk, defn):
  attk.modifiers["spd"] += 2

def superpower(attk, defn):
  attk.modifiers["atk"] -= 1
  attk.modifiers["defn"] -= 1

def ironhead(attk, defn):
  if flip(1):
    defn.flinch = True

def rockslide(attk, defn):
  if flip(0.3):
    defn.flinch = True

def swordsdance(attk, defn):
  attk.modifiers["atk"] += 2

def dragondance(attk, defn):
  attk.modifiers["atk"] += 1
  attk.modifiers["spd"] += 1

def dragonclaw(attk, defn):
  pass

def roost(attk, defn):
  attk.curHp += math.floor(attk.hp / 2)
  attk.grounded = True



secondarydict = {
  "earthquake":earthquake,
  "psychic":psychic,
  "shadow ball":shadowball,
  "focus blast":focusblast,
  "dazzling gleam":dazzlinggleam,
  "v-create":vcreate,
  "bolt strike":boltstrike,
  "final gambit":finalgambit,
  "zen headbutt":zenheadbutt,
  "liquidation":liquidation,
  "crunch":crunch,
  "poison jab":poisonjab,
  "x-scissor":xscissor,
  "bug bite":bugbite,
  "bullet punch":bulletpunch,
  "agility":agility,
  "superpower":superpower,
  "iron head":ironhead,
  "rock slide":rockslide,
  "swords dance":swordsdance,
  "dragon dance":dragondance,
  "dragon claw":dragonclaw,
  "roost":roost,
}

