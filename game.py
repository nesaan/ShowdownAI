from battle import *
from baseai import *

battle = Battle(BaseAi(), "")
print(battle)
ai2 = BaseAi()
moves = 0
while not battle.isGameOver():
  #action = int(input())
  #actionspace = battle.active1.moves + battle.team1
  battle.makeMove(ai2.chooseAction(battle.active1, battle.team1, battle.active2, battle.team2))
  moves += 1
  print(battle)


print(moves)