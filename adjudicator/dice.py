from config import log
import config
import random

class Dice:

	def __init__(self):
		self.reset()
		
	def reset(self):
		self.die_1 = None
		self.die_2 = None
		self.double = False
		self.double_counter = 0

	def roll(self,ignore=False,dice=None):
		"""Roll two fair six-sided die and store (1) the sum of the roll, (2) an indicator of whether it was a double
		roll and (3) a counter of the number of consecutive double rolls."""
		
		if dice is not None:
			log("dice","Choosing the debug dice")
			roll = dice
		else:
			roll = [random.randint(1, 6), random.randint(1, 6)]
		
		self.die_1 = roll[0]
		self.die_2 = roll[1]
		self.double = roll[0] == roll[1]
		if not ignore:
			self.double_counter += self.double
		
		log("dice",'Roll a {die_1} and a {die_2}'.format(die_1=roll[0], die_2=roll[1]))