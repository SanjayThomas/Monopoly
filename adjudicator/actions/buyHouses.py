from config import log
from state import Phase
from constants import board
from utils import typecast
from actions.constants import BOARD_SIZE,MEDAVE_BUILDCOST,MONOPOLY_GROUPS

# TODO: houses,hotels remaining
def publish(context):
	# call agent if:
	# not bankrupt
	# has all properties in atleast one monopoly group
	# has money required to buy atleast one of the least expensive houses
	state = context.state
	agentId = context.bsmAgentId

	if state.bankrupt[agentId] or not canBuyHouses(state,agentId):
		return []

	log("bsm","Agent {} can buy houses/hotels!".format(agentId))
	return [agentId]

# responses is a dict mapping agentId to response
def subscribe(context, responses):
	state = context.state
	agentId,sequence = list(responses.items())[0]
	
	# check if given buying sequence is valid and apply it if it is
	# for now, if any entry in the sequence is invalid, the whole sequence is invalidated
	if validateBuyingSequence(sequence) and state.isBuyingSequenceValid(agentId,sequence):
		log("bsm","The buying sequence {} for {} is valid.".format(sequence,agentId))
		playerCash = state.getCash(agentId)
		for propertyId,houses in sequence:
			houseCount = state.getNumberOfHouses(propertyId)
			houseCount += houses
			playerCash -= board[propertyId]['build_cost']*houses
			state.setNumberOfHouses(propertyId,houseCount)
		state.setCash(agentId,playerCash)
	
	noPlayers = len(context.state.players)
	nextIndex = (state.getPlayerIndex(agentId) + 1) % noPlayers
	nextAgentId = state.getPlayerId(nextIndex)
	currentAgentId = state.getCurrentPlayerId()
	context.bsmAgentId = nextAgentId

	if nextAgentId == currentAgentId:
		# buying houses is done for all agents in this turn
		return Phase.END_TURN
	
	# do unmortgage for the next agent
	return Phase.UNMORTGAGE

def canBuyHouses(state, agentId):
	leastPrice = 201
	playerCash = state.getCash(agentId)
	
	if playerCash < MEDAVE_BUILDCOST:
		return False
	
	for monopolyGroup in MONOPOLY_GROUPS:
		count = 0
		for mId in monopolyGroup:
			if state.rightOwner(agentId, mId):
				count += 1
		if count == len(monopolyGroup):
			buildCost = board[monopolyGroup[0]]['build_cost']
			if buildCost < leastPrice:
				leastPrice = buildCost
	
	if leastPrice == 201 or leastPrice > playerCash:
		return False
	
	return True

# checks if response from agent follows proper structure
def validateBuyingSequence(sequence):
	if not ( isinstance(sequence, list) or isinstance(sequence, tuple) ) or len(sequence) == 0:
		return False
	
	for index,prop in enumerate(sequence):
		if not ( isinstance(prop, list) or isinstance(prop, tuple) ) or len(prop) < 2:
			return False
		
		arg1 = typecast(prop[0],int,-1)
		arg2 = typecast(prop[1],int,-1)
		sequence[index] = (arg1,arg2)
		if sequence[index][0]<0 or sequence[index][0]>BOARD_SIZE-1:
			return False
		if sequence[index][1]<0 or sequence[index][1]>5:
			return False

	return True