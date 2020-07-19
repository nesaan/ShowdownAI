import random

class BaseAi:
  # returns a poke if wish to switch
  # returns a move if wish to use move
  def chooseAction(self, myactive, myteam, oppactive, oppteam):
    prefS = random.choices([0, 1], [0.75, 0.25])
    choices = [x for x in myteam if x.curHp > 0 and x != myactive]
    if not choices and myactive.curHp <= 0:
      raise Exception("No options")

    if myactive.curHp <= 0 or prefS and choices:
      return random.choice(choices)
    else:
      return random.choice(myactive.moves)
