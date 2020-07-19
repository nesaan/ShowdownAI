from battle import *
from baseai import *

battle = Battle(BaseAi())
print(battle)

while not battle.isGameOver():
  action = int(input())
  actionspace = battle.active1.moves + battle.team1

  battle.makeMove(actionspace[action])
  print(battle)
