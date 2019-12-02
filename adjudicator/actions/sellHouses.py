from config import log
from constants import board
from actions.constants import BOARD_SIZE
from state import Phase
from utils import typecast

def publish(context):
	# call agent if:
	# not bankrupt
	# has houses on any property
	agentId = context.bsmAgentId
	state = context.state

	if state.bankrupt[agentId] or (getHousesCount(state,agentId) == 0):
		return []

	log("game","Agent {} has houses/hotels to sell!".format(agentId))
	
	return [agentId]

# responses is a dict mapping agentId to response
def subscribe(context, responses):
	state = context.state
	agentId,sellingSequence = list(responses.items())[0]
	
	# check if given selling sequence is valid and apply it if it is
	# for now, if any entry in the sequence is invalid, the whole sequence is invalidated
	if validateSellingSequence(sellingSequence) and state.isSellingSequenceValid(agentId,sellingSequence):
		log("game","The selling sequence for agent {} is valid.".format(agentId))
		# handle selling
		cash = 0
		for propertyId,houses in sellingSequence:
			space = board[propertyId]
			houseCount = state.getNumberOfHouses(propertyId)
			houseCount -= houses
			cash += int(space['build_cost']*0.5*houses)
			state.setNumberOfHouses(propertyId,houseCount)
		
		state.addCash(agentId,cash)

	return Phase.TRADE

# total number of houses, counting a hotel as 5 houses
def getHousesCount(state, agentId):
	housesCount = 0
	for p in state.properties:
		if state.rightOwner(agentId, p.propertyId):
			housesCount += state.getNumberOfHouses(p.propertyId)

	return housesCount

# checks if response from agent follows proper structure
def validateSellingSequence(sequence):
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