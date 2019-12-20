from config import log
from constants import board
from state import Phase
from utils import typecast
from actions.constants import BOARD_SIZE

# does the agent have any properties he can mortgage/unmortgage?
# the result of this function is the list of agents for whom we should
# call mortgage/unmortgage
def publish(context):
	agentId = context.bsmAgentId
	state = context.state

	if state.bankrupt[agentId]:
		return []
	
	if state.getPhase() == Phase.MORTGAGE:
		candidates = []
		for p in state.properties:
			if canMortgage(p.propertyId,agentId,state):
				candidates.append(p.propertyId)
		if len(candidates) == 0:
			return []
		log("bsm","Agent {} has properties to mortgage!".format(agentId))
	else:
		candidates = []
		for p in state.properties:
			if canUnmortgage(p.propertyId,agentId,state):
				candidates.append(p.propertyId)
		if len(candidates) == 0:
			return []
		log("bsm","Agent {} has properties to unmortgage!".format(agentId))
	
	return [agentId]

# responses is a dict mapping agentId to response
def subscribe(context, responses):
	state = context.state
	agentId,sequence = list(responses.items())[0]
	currentPhase = state.getPhase()
	
	# for now, if any entry in the sequence is invalid, the whole sequence is invalidated
	if validateMortgageSequence(sequence):
		if currentPhase == Phase.MORTGAGE:
			res = handleMortgage(state,agentId,sequence)
		else:
			res = handleUnmortgage(context,agentId,sequence)
			log("bsm","Result of unmortgage sequence by agent {}: {}".format(agentId,res))

	if currentPhase == Phase.MORTGAGE:
		return Phase.SELL_HOUSES
	return Phase.BUY_HOUSES

# checks if response from agent follows proper structure
def validateMortgageSequence(sequence):
	if not ( isinstance(sequence, list) or isinstance(sequence, tuple) ) or len(sequence) == 0:
		return False
	
	sequence = [typecast(prop,int,-1) for prop in sequence]
	return True

def canMortgage(propertyId,playerId,state):
	if propertyId<0 or propertyId>BOARD_SIZE-1:
		return False
	if not state.rightOwner(playerId,propertyId):
		return False
	if state.isPropertyMortgaged(propertyId):
		return False
	if state.getNumberOfHouses(propertyId)>0:
		return False
	monopolyProps = board[propertyId]["monopoly_group_elements"]
	for monopolyProp in monopolyProps:
		if state.getNumberOfHouses(monopolyProp)>0:
			return False
	return True

def canUnmortgage(propertyId,playerId,state):
	if propertyId<0 or propertyId>BOARD_SIZE-1:
		return False
	if not state.rightOwner(playerId,propertyId):
		return False
	if not state.isPropertyMortgaged(propertyId):
		return False
	return True

# If property is mortgaged, player gets back 50% of the price.
# If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
# If the player tries to mortgage an invalid property, entire operation fails.
def handleMortgage(state,playerId,properties):
	cash = 0
	
	for propertyId in properties:
		if not canMortgage(propertyId,playerId,state):
			log("bsm","Mortgage request {} from {} failed.".format(properties,playerId))
			return False

		mortagePrice = int(board[propertyId]['price']/2)
		cash += mortagePrice
	
	# actually applying state changes
	for propertyId in properties:
		state.setPropertyMortgaged(propertyId,True)
	state.addCash(playerId,cash)
	log("bsm","Agent {} mortgaged {} to get ${}".format(playerId,properties,cash))
	return True

# If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
# If there is an unmortgaged property, its ignored
def handleUnmortgage(context,playerId,properties):
	state = context.state
	playerCash = state.getCash(playerId)
	
	for propertyId in properties:
		if not canUnmortgage(propertyId,playerId,state):
			log("bsm","Unmortgage request {} from {} failed.".format(properties,playerId))
			return False
		
		unmortgagePrice = int(board[propertyId]['price']/2)   
		if propertyId in context.mortgagedDuringTrade:
			context.mortgagedDuringTrade.remove(propertyId)
		else:
			unmortgagePrice = int(unmortgagePrice*1.1)

		if playerCash < unmortgagePrice:
			return False
		
		playerCash -= unmortgagePrice 
	
	# actually applying state changes
	for propertyId in properties:
		state.setPropertyMortgaged(propertyId,False)
	state.setCash(playerId,playerCash)
	log("bsm","Agent {} unmortgaged {}.".format(playerId,properties))
	return True
