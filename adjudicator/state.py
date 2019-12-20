import random
from collections import OrderedDict
from constants import board
import json
from copy import deepcopy

INITIAL_CASH = 1500
MAX_HOUSES = 32
MAX_HOTELS = 12
NUMBER_OF_PROPERTIES = 42

class Property:
	def __init__(self,houses,mortgaged,ownerId,propertyId):
		self.houses = houses # value in range 0-5
		self.mortgaged = mortgaged #boolean
		self.ownerId = ownerId
		self.propertyId = propertyId 
	
	def convert(self):
		return {"houses":self.houses,"mortgaged":self.mortgaged,"ownerId":self.ownerId}

class State:
	def __init__(self,playerIds,timePerMove,properties=None):
		#List of id's of all the agents in the order in which the game will take place.
		self.players = list(playerIds)
		self.TOTAL_NO_OF_PLAYERS = len(playerIds)
		self.timePerMove = timePerMove
		
		self.turnNumber = -1
		self.currentPlayerId = None
		
		if properties == None:
			self.properties = [Property(0,False,None,i) for i in range(NUMBER_OF_PROPERTIES)]
		else:
			#no validation here
			self.properties = properties
		self.positions = {}
		self.cash = {}
		self.bankrupt = {}
		self.phase = Phase.START_GAME
		self.phasePayload = None
		
		self.jailCounter = {}
		self.reason_for_loss = {}
		self.turn_of_loss = {}
		self.creditor = {}
		for playerId in self.players:
			self.positions[playerId] = 0
			self.cash[playerId] = INITIAL_CASH
			self.bankrupt[playerId] = False
			self.jailCounter[playerId] = 0
			self.reason_for_loss[playerId] = None
			self.turn_of_loss[playerId] = -1
			self.creditor[playerId] = None
	
	"""The index of the player in the players array"""
	"""This represents the order of play for the player"""
	def getCurrentPlayerIndex(self):
		return self.turnNumber % self.TOTAL_NO_OF_PLAYERS
	
	"""Actual Player Id set inside the agent accessible as agent.id attribute"""
	def getCurrentPlayerId(self):
		return self.players[self.getCurrentPlayerIndex()]
	
	def getPlayerId(self,playerIndex):
		if isinstance(playerIndex,int) and playerIndex>=0 and playerIndex<len(self.players):
			return self.players[playerIndex]
		else:
			return None
	
	def getPlayerIndex(self,playerId):
		try:
			return self.players.index(playerId)
		except:
			print(str(playerId)+" is not a valid agentId.")
			return -1
	
	"""TURN"""
	def getTurn(self):
		return self.turnNumber
	
	def updateTurn(self):
		self.turnNumber+=1
		self.currentPlayerId = self.getCurrentPlayerId()
	
	"""POSITION"""
	def getPosition(self,playerId):
		return self.positions[playerId]
	
	def setPosition(self,playerId,position):
		self.positions[playerId] = position
	
	"""CASH"""
	def getCash(self,playerId):
		return self.cash[playerId]
		
	def setCash(self,playerId,cash):
		self.cash[playerId] = cash

	# only call if playerId gets cash from bank
	def addCash(self,playerId,cash):
		# pay debts if any
		if self.creditor[playerId] is not None:
			if abs(self.cash[playerId]) > cash:
				# some debt remains
				self.cash[self.creditor[playerId]] += cash
			else:
				# debt cleared
				self.cash[self.creditor[playerId]] += abs(self.cash[playerId])
				self.creditor[playerId] = None

		self.cash[playerId] += cash

	def addDebt(self,playerId,cash,creditor=None):
		# playerId owes cash to creditor
		if creditor is not None:
			if self.cash[playerId] - cash < 0:
				# give all available cash to the creditor
				# playerId's cash would now be -ve.
				# this represents the cash they owe to creditor
				self.creditor[playerId] = creditor
				self.addCash(creditor,self.cash[playerId])
			else:
				self.addCash(creditor,cash)
			
		self.cash[playerId]-=cash

	def clearDebts(self):
		for playerId in self.getLivePlayers():
			# TODO: redistribution of properties
			if self.getCash(playerId) < 0:
				self.markPlayerLost(playerId, Reason.BANKRUPT)
	
	"""BANKRUPT"""
	def hasPlayerLost(self,playerId):
		return self.bankrupt[playerId]
	
	def markPlayerLost(self,playerId,reason):
		self.bankrupt[playerId] = True
		self.reason_for_loss[playerId] = reason
		self.turn_of_loss[playerId] = self.turnNumber
	
	def getTurnOfLoss(self,playerId):
		return self.turn_of_loss[playerId]
	
	"""PHASE"""
	def getPhase(self):
		return self.phase
		
	def setPhase(self,phase):
		self.phase = phase
	
	"""PHASE PAYLOAD"""
	def getPhasePayload(self):
		return self.phasePayload
		
	def setPhasePayload(self,phasePayload):
		self.phasePayload = phasePayload
		
	"""JAIL COUNTER"""
	def getJailCounter(self,playerId):
		return self.jailCounter[playerId]
	
	def incrementJailCounter(self,playerId):
		self.jailCounter[playerId]+=1
	
	def resetJailCounter(self,playerId):
		self.jailCounter[playerId]=0
	
	"""PROPERTIES"""
	
	"""OWNERSHIP FUNCTIONS"""
	def isPropertyOwned(self,propertyId):
		return self.properties[propertyId].ownerId is not None
	
	def setPropertyUnowned(self,propertyId):
		self.properties[propertyId].ownerId = None
		self.properties[propertyId].houses = 0
		self.properties[propertyId].mortgaged = False
		
	def getPropertyOwner(self,propertyId):
		return self.properties[propertyId].ownerId
	
	def setPropertyOwner(self,propertyId,playerId):
		self.properties[propertyId].ownerId = playerId
		# If a property changes ownership, it should start with no houses
		self.properties[propertyId].houses = 0
	
	# logic to be changed
	def rightOwner(self,playerId,propertyId):
		return self.getPropertyOwner(propertyId) == playerId
	
	"""MORTGAGE FUNCTIONS"""
	def isPropertyMortgaged(self,propertyId):
		return self.properties[propertyId].mortgaged
	
	def setPropertyMortgaged(self,propertyId,mortgaged):
		self.properties[propertyId].mortgaged = mortgaged
	
	"""HOUSES FUNCTIONS"""
	def getNumberOfHouses(self,propertyId):
		return self.properties[propertyId].houses
	
	def setNumberOfHouses(self,propertyId,count):
		self.properties[propertyId].houses = count
	
	"""HOTEL FUNCTIONS"""
	"""Checks if hotels can be built on the given set of property ids."""
	def isBuyingHotelSequenceValid(self,playerId,propertySequence):
		for propertyId in propertySequence:
			currentProperty = self.properties[propertyId]
			if (currentProperty.ownerId!=playerId) or (currentProperty.mortgaged) or (currentProperty.houses!=4):
				return False
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyProperty = self.properties[monopolyPropertyId]
				if (monopolyProperty.ownerId!=playerId) or (monopolyProperty.mortgaged) or (monopolyProperty.houses<4):
					return False
		return True
	
	"""Buys hotels on the property ids in the given sequence. Assumes that these are valid properties for hotels."""
	def buyHotelSequence(self,playerId,sequence):
		playerCash = self.getCash(playerId)
		for propertyId in sequence:
			playerCash -= board[propertyId]["build_cost"]
			self.setNumberOfHouses(propertyId, 5)
		self.setCash(playerId, playerCash)
	
	"""
	Checks if the properties are streets,
	that the player owns all the properties in the monopoly and that they are all unmortgaged.
	and that houses are being built evenly.
	"""
	def isSequenceValid(self,playerId,propertySequence,sign):
		propertiesCopy = deepcopy(self.properties)
		for propertyId,housesCount in propertySequence:
			if board[propertyId]['class']!="Street":
				return False
			
			currentProperty = propertiesCopy[propertyId]
			if (currentProperty.ownerId!=playerId) or (currentProperty.mortgaged):
				return False
			
			for monopolyId in board[propertyId]["monopoly_group_elements"]:
				monopolyProperty = propertiesCopy[monopolyId]
				if (monopolyProperty.ownerId!=playerId) or (monopolyProperty.mortgaged):
					return False
			
			newHousesCount = currentProperty.houses+(sign*housesCount)
			if (newHousesCount>5) or (newHousesCount<0):
				return False
			propertiesCopy[propertyId].houses+=(sign*housesCount)
		
		for propertyId,_ in propertySequence:
			houses = propertiesCopy[propertyId].houses
			for monopolyId in board[propertyId]["monopoly_group_elements"]:
				monopolyHouses = propertiesCopy[monopolyId].houses
				if abs(monopolyHouses-houses)>1:
					return False
		return True
	
	def isBuyingSequenceValid(self, playerId,propertySequence):
		return self.isSequenceValid(playerId, propertySequence, 1)
		
	def isSellingSequenceValid(self,playerId,propertySequence):
		return self.isSequenceValid(playerId, propertySequence, -1)
	
	def evaluateBuyingHousesSequence(self,sequence):
		totalCurrentHouses = 0
		totalNewHouses = 0
		for propertyId,constructions in sequence:
			currentHouses = self.properties[propertyId].houses
			#if currentHouses==5: currentHouses=0
			totalCurrentHouses+=currentHouses
			
			newHouses = currentHouses+constructions
			totalNewHouses+=newHouses
		return (totalNewHouses-totalCurrentHouses)
	
	def evaluateSellingSequence(self,sequence):
		totalCurrentHouses = 0
		totalNewHouses = 0
		totalCurrentHotels = 0
		totalNewHotels = 0
		
		for propertyId,constructions,hotel in sequence:
			housesCounter = self.properties[propertyId].houses
			if housesCounter<5:
				currentHouses = housesCounter
				currentHotels = 0
			else:
				currentHouses = 0
				currentHotels = 1
			totalCurrentHouses+=currentHouses
			totalCurrentHotels+=currentHotels
			
			if hotel: constructions+=1
			newHousesCounter = housesCounter-constructions
			if newHousesCounter<5:
				newHouses = newHousesCounter
				newHotels = 0
			else:
				newHouses = 0
				newHotels = 1
			totalNewHouses+=newHouses
			totalNewHotels+=newHotels
		return (totalNewHouses-totalCurrentHouses,totalNewHotels-totalCurrentHotels)
			
	def getHousesRemaining(self):
		houses = MAX_HOUSES
		for prop in self.properties:
			if (prop.houses>0) and (prop.houses<5): houses -= prop.houses
		return houses

	def getHotelsRemaining(self):
		hotels = MAX_HOTELS
		for prop in self.properties:
			if (prop.houses==5): hotels -= 1
		return hotels
	
	def getOwnedProperties(self, playerId):
		return [propertyId for propertyId in range(NUMBER_OF_PROPERTIES)
			if self.properties[propertyId].ownerId==playerId]

	def getConstructionValue(self,propertyId):
		return constants.board[propertyId]["build_cost"]

	""" Bunch of utilities """
	def getLivePlayers(self):
		return [playerId for playerId in self.players if not self.hasPlayerLost(playerId)]

	def getNextPlayer(self,currentPlayer):
		try:
			currentPlayerIndex = self.players.index(currentPlayer)
			return self.players[(currentPlayerIndex + 1) % TOTAL_NO_OF_PLAYERS]
		except e:
			# player not found
			raise e
	
	def toDict(self):
		return OrderedDict([ ("player_ids", self.players),
					("current_player_id", self.currentPlayerId),
					("turn_number", self.turnNumber),
					("properties", [prop.convert() for prop in self.properties]),
					("player_board_positions", self.positions),
					("player_cash",self.cash),
					("player_loss_status", self.bankrupt),
					("phase", self.phase),
					("phase_payload", self.phasePayload),
					("timeout",self.timePerMove)])
	
	def toJson(self):
		return json.dumps(self.toDict())

	def __str__(self):
		return str(self.toJson())
	
class Phase:
	# these are mandatory phases
	START_GAME         = 'START_GAME' # broadcast but mandatory
	START_TURN         = 'START_TURN' # optional
	JAIL               = 'JAIL'

	JAIL_RESULT        = 'JAIL_RESULT' # optional
	
	DICE_ROLL          = 'DICE_ROLL' # optional
	CHANCE_CARD        = 'CHANCE_CARD' # optional, which chance card was drawn
	COMMUNITY_CHEST    = 'COMMUNITY_CHEST' # optional
	MORTGAGE           = 'MORTGAGE'
	UNMORTGAGE         = 'UNMORTGAGE'
	
	MORTGAGE_RESULT    = 'MORTGAGE_RESULT' # optional,returns tuple of booleans saying which requests were successful
	UNMORTGAGE_RESULT  = 'UNMORTGAGE_RESULT'

	SELL_HOUSES        = 'SELL_HOUSES'
	
	SELL_HOUSES_RESULT = 'SELL_HOUSES_RESULT'
	
	BUY                = 'BUY'
	
	BUY_RESULT         = 'BUY_RESULT' # broadcast whether user is going to buy or auction
	
	AUCTION            = 'AUCTION'
	
	AUCTION_RESULT     = 'AUCTION_RESULT' # optional
	TRADE              = 'TRADE'
	TRADE_RESPONSE     = 'TRADE_RESPONSE'
	TRADE_RESULT       = 'TRADE_RESULT' # optional
	
	BUY_HOUSES         = 'BUY_HOUSES'
	
	BUY_HOUSES_RESULT  = 'BUY_HOUSES_RESULT' # optional
	
	END_TURN           = 'END_TURN' # optional
	END_GAME           = 'END_GAME'


# Phase Payload definition:
# START_GAME :
# nil
# nil
# JAIL :
# how many turns you have been in jail
# ('c',<card no>) or 'p' or 'd'
# BUY  : nil
# true = buy, false = auction
# BUY_RESULT:
# true = buy, false = auction
# nil
# AUCTION:
# nil
# int bid value
# MORTGAGE:
# nil
# [props to be (un)mortgaged]
# SELL_HOUSES:
# nil
# [(prop,# houses),...]
# TRADE:
# nil
# [(agentId, cashOffer, cashGet, propsOffer, propsGet)]
# TRADE_RESPONSE:
# (agentId, cashOffer, cashGet, propsOffer, propsGet)
# true = accept, false = reject
# BUY_HOUSES:
# nil
# [(prop,# houses),...]
# END_GAME:
# nil
# nil

# response for all these are nil
# START_TURN
# nil
# JAIL_RESULT
# true = out of jail, false = jailed
# DICE_ROLL
# (die1,die2)
# CHANCE_CARD
# cardId
# COMMUNITY_CHEST
# cardId
# AUCTION_RESULT
# agentId of winner
# MORTGAGE_RESULT
# [true/false,...]
# SELL_HOUSES_RESULT
# [true/false,...]
# TRADE_RESULT
# [true/false,...]
# BUY_HOUSES_RESULT
# [true/false,...]
# END_TURN
# nil
# BANKRUPT
# [agentIds bankrupted this turn]

	
"""
The reason for victory:
0 = Greater assets at the end of specified number of turns.
1 = Timed Out (Could also pass while doing which action did the timeout occur)
2 = Bankruptcy from Debt to Opponent or Bank
3 = Bankruptcy from being unable to pay the fine for Jail on the third turnNumber in Jail.
"""
class Reason:
	ASSETS = "Greater Assets"
	TIMEOUT = "Timeout"
	BANKRUPT = "Bankruptcy"
	
#state = State(["1","2"])
#print(state.toJson())
#for value in json.loads(state.toJson()):
#	print(value)
#	print(value)