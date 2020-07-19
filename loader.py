import json
import copy

class Library:
  def __init__(self, name):
    with open(name + 'Library.json') as libfile:
      self.data = json.load(libfile)
  
  def loadFromName(self, container):
    obj = self.data[container.name]
    for key,value in obj.items():
      setattr(container, key, value)

POKE_LIB = Library('Poke')
MOVE_LIB = Library("Move")