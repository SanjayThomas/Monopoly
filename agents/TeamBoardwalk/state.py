import random
from collections import namedtuple
import json

from .board import board, MAX_HOUSES, MAX_HOTELS, groups, Group

StateTuple = namedtuple("StateTuple", "current_player turn properties positions money phase phaseData debt")
TradeData = namedtuple("TradeData", "moneyOffered propertiesOffered moneyRequested propertiesRequested")

# makes it possible to print a state without printing all of the past states
class StateList(list):
	def __str__(self):
		return str(len(self)) + " past states"

	def __repr__(self):
		return str(len(self)) + " past states"

	def __deepcopy__(self, memo):
		return StateList(self)

class Property:
	def __init__(self, id, owned, owner, houses, mortgaged):
		self.id = id
		self.data = board[id] if id < 40 else None
		self.owned = owned
		self.owner = owner
		# 5 houses = hotel
		self.houses = houses
		self.mortgaged = mortgaged
	
	def __str__(self):
		return str(self.id)+","+str(self.owned)+","+str(self.owner)+","+str(self.houses)+","+str(self.mortgaged)
	
	# speed up deepcopy of state
	def __deepcopy__(self, memo):
		return Property(self.id, self.owned, self.owner, self.houses, self.mortgaged)

class Debt:
	def __init__(self,bank,otherPlayers):
		self.bank = bank
		self.otherPlayers = otherPlayers
		
	def getTotalDebt(self):
		debt = self.bank
		for playerId,playerDebt in self.otherPlayers.items():
			debt += playerDebt
		return debt

class State:
	def __init__(self, stateTuple):
		if stateTuple:
			stateTuple = json.loads(stateTuple)
			self.player_ids = stateTuple['player_ids']
			self.current_player_id = stateTuple['current_player_id']
			self.turn = stateTuple['turn_number']
			self.properties = []
			for id, value in enumerate(stateTuple['properties']):
				owned = value['owned']
				owner = value['ownerId']
				mortgaged = value['mortgaged']
				houses = value['houses']
				if value['hotel']: houses=5
				self.properties.append(Property(id, owned, owner, houses, mortgaged))
			
			self.positions = stateTuple['player_board_positions']
			self.money = stateTuple['player_cash']
			self.bankrupt = stateTuple['player_loss_status']
			self.phase = stateTuple['current_phase_number']
			self.phaseData = stateTuple['phase_payload']
			self.debt = {}
			for id, value in stateTuple['player_debts'].items():
				bank = value['bank']
				otherPlayers = value['otherPlayers']
				self.debt[id] = Debt(bank,otherPlayers)
	
	def getOpponents(self,id):
		return [playerId for playerId in self.player_ids if not playerId==id]
	
	def getNextRoll(self):
		if self.diceRolls:
			return self.diceRolls.pop(0)
		if self.diceRolls == []:
			raise GameOverException
		return random.randint(1, 6), random.randint(1, 6)

	def getHousesRemaining(self):
		houses = MAX_HOUSES
		for prop in self.properties:
			if prop.houses < 5: houses -= prop.houses
		return houses

	def getHotelsRemaining(self):
		hotels = MAX_HOTELS
		for prop in self.properties:
			if prop.houses == 5: hotels -= 1
		return hotels

	def getGroupProperties(self, group):
		if group<0 or group>=len(groups):
			print(group)
		for id in groups[group]:
			if id<0 or id>len(self.properties):
				print("id: ",id)	
		return [self.properties[id] for id in groups[group]]

	def getOwnedProperties(self, player):
		return [prop for prop in self.properties if prop.owned and prop.owner == player and prop.id < 40]

	def getOwnedGroupProperties(self, player):
		owned = self.getOwnedProperties(player)
		return [prop for prop in owned if self.playerOwnsGroup(player, prop.data.group)]

	def getOwnedGroups(self, player):
		return [group for group in range(0, 10) if self.playerOwnsGroup(player, group)]

	def getOwnedBuildableGroups(self, player):
		return [group for group in range(0, 8) if self.playerOwnsGroup(player, group)]

	def playerOwnsGroup(self, player, group):
		for prop in self.getGroupProperties(group):
			if not prop.owned or not prop.owner == player: return False
		return True

	def getRailroadCount(self, player):
		count = 0
		for prop in self.getGroupProperties(Group.RAILROAD):
			if prop.owned and prop.owner == player: count += 1
		return count

	def makePayment(self, player1, player2, amount):
		if player1 != -1: self.debt[player1] += amount
		if player2 != -1: self.money[player2] += amount

	def toTuple(self):
		return StateTuple(self.current_player_id, self.turn, [str(prop) for prop in self.properties], self.positions,
						  self.money, self.phase, self.phaseData, self.debt)

	def __str__(self):
		return str(self.toTuple())

class Phase:
	NO_ACTION = 0
	TRADE = 1
	DICE_ROLL = 2
	BUYING = 3
	AUCTION = 4
	PAYMENT = 5
	JAIL = 6
	CHANCE_CARD = 7
	COMMUNITY_CHEST_CARD = 8

class GameOverException(Exception):
	pass
