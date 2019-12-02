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
	agentId,sequence = list(responses.items())[0]
	currentPhase = state.getPhase()
	
	# for now, if any entry in the sequence is invalid, the whole sequence is invalidated
	if validateMortgageSequence(sequence):
		if currentPhase == Phase.MORTGAGE:
			res = handleMortgage(context,agentId,sequence)
			log("game","Result of mortgage sequence by agent {}: {}".format(agentId,res))
		else:
			res = handleUnmortgage(context,agentId,sequence)
			log("game","Result of unmortgage sequence by agent {}: {}".format(agentId,res))

	if currentPhase == Phase.MORTGAGE:
		return Phase.SELL_HOUSES
	return Phase.BUY_HOUSES

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
	cash = 0
	
	for propertyId in properties:
		if not state.rightOwner(playerId,propertyId):
			return False
		
		if not state.isPropertyMortgaged(propertyId):
			#There should be no houses on a property to be mortgaged or in any other property in the monopoly.
			if state.getNumberOfHouses(propertyId)>0:
				return False
			space = board[propertyId]
			for monopolyPropertyId in space["monopoly_group_elements"]:
				if state.getNumberOfHouses(propertyId)>0:
					return False

			mortagePrice = int(board[propertyId]['price']/2)
			cash += mortagePrice
			log("bsm","Agent {} wants to mortgage {}".format(playerId,propertyId))
	
	# actually applying state changes
	for propertyId in properties:
		state.setPropertyMortgaged(propertyId,True)
	state.addCash(playerId,cash)

	return True

# If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
# If there is an unmortgaged property, its ignored
def handleUnmortgage(context,playerId,properties):
	state = context.state
	playerCash = state.getCash(playerId)
	
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
	
	# actually applying state changes
	for propertyId in properties:
		state.setPropertyMortgaged(propertyId,False)
	state.setCash(playerId,playerCash)

	return True