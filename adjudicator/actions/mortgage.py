from config import log
from constants import board
from state import Phase
from utils import typecast
from actions.constants import BOARD_SIZE

def publish(context):
	# call agent if:
	# not bankrupt
	# has houses on any property
	agentId = context.bsmAgentId
	state = context.state

	if state.bankrupt[agentId] or (getPropertiesCount(state,agentId) == 0):
		return []
	
	log("game","Agent {} has properties to (un)mortgage!".format(agentId))
	
	return [agentId]

# responses is a dict mapping agentId to response
def subscribe(context, responses):
	state = context.state
	
	# check if given selling sequence is valid and apply it if it is
	# for now, if any entry in the sequence is invalid, the whole sequence is invalidated
	for agentId,mortgageSequence in responses.items():
		if validateMortgageSequence(mortgageSequence):
			res = handleMortgage(context,agentId,mortgageSequence)
			log("game","Result of mortgage sequence by agent {}: {}".format(agentId,res))

	return Phase.SELL_HOUSES

# is the current player on an unowned property?
# this would mean there is a buy/auction decision to be made in this turn
def isBuyDecision(state):
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	propertyClass = board[playerPosition]['class']
	
	if propertyClass == 'Street' or propertyClass == 'Railroad' or propertyClass == 'Utility':
		isPropertyOwned = state.isPropertyOwned(playerPosition)
		if not isPropertyOwned:
			return True
	
	return False

# total number of properties owned by the agent
def getPropertiesCount(state, agentId):
	propCount = 0
	for p in state.properties:
		if state.rightOwner(agentId, p.propertyId):
			propCount += 1

	return propCount

# checks if response from agent follows proper structure
def validateMortgageSequence(sequence):
	if not ( isinstance(sequence, list) or isinstance(sequence, tuple) ) or len(sequence) == 0:
		return False
	
	sequence = [typecast(prop,int,-1) for prop in sequence]
	for prop in sequence:
		if prop<0 or prop>BOARD_SIZE-1:
			return False

	return True

# If property is mortgaged, player gets back 50% of the price.
# If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
# If the player tries to mortgage an invalid property, entire operation fails.
def handleMortgage(context,playerId,properties):
	state = context.state
	playerCash = state.getCash(playerId)
	mortgageRequests = []
	unmortgageRequests = []
	
	for propertyId in properties:
		if not state.rightOwner(playerId,propertyId):
			return False
		
		if state.isPropertyMortgaged(propertyId):
			unmortgagePrice = int(board[propertyId]['price']/2)   

			if propertyId in context.mortgagedDuringTrade:
				context.mortgagedDuringTrade.remove(propertyId)
			else:
				unmortgagePrice = int(unmortgagePrice*1.1)

			if playerCash < unmortgagePrice:
				return False
			
			playerCash -= unmortgagePrice 
			
			log("bsm","Agent {} wants to unmortgage {}".format(playerId,propertyId))
		else:
			#There should be no houses on a property to be mortgaged or in any other property in the monopoly.
			if state.getNumberOfHouses(propertyId)>0:
				return False
			space = board[propertyId]
			for monopolyPropertyId in space["monopoly_group_elements"]:
				if state.getNumberOfHouses(propertyId)>0:
					return False

			mortagePrice = int(board[propertyId]['price']/2)
			playerCash += mortagePrice
			log("bsm","Agent {} wants to mortgage {}".format(playerId,propertyId))
	
	# actually applying state changes
	for propertyId in properties:
		state.setPropertyMortgaged(propertyId,not state.isPropertyMortgaged(propertyId))
	state.setCash(playerId,playerCash)

	return True