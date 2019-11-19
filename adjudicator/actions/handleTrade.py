from utils import typecast,check_valid_cash
from constants import board
from state import Phase
from config import log
from actions.constants import MAX_TRADES, BOARD_SIZE

def publish(context):
	state = context.state
	# should start with the current player's ID always
	agentId = context.bsmAgentId

	if state.bankrupt[agentId]:
		return []

	log("game","Agent {} can trade!".format(agentId))
	
	return [agentId]
	
def subscribe(context,responses):
	state = context.state
	agentId,tradeAction = list(responses.items())[0]

	if validateTradeAction(context,agentId,tradeAction):
		otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = tradeAction
		tradeRequest = (agentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest)
		state.setPhasePayload(tradeRequest)
		context.tradeReceiver = otherAgentId
		return Phase.TRADE_RESPONSE

	context.tradeCounter+=1
	if context.tradeCounter < MAX_TRADES:
		# continue trades for the same agent
		return Phase.TRADE

	noPlayers = len(context.PLAY_ORDER)
	nextIndex = (state.getPlayerIndex(agentId) + 1) % noPlayers
	nextAgentId = state.getPlayerId(nextIndex)
	currentAgentId = state.getCurrentPlayerId()
	context.bsmAgentId = nextAgentId

	# resetting trade counter for other agents
	context.tradeCounter = 0

	if isBuyDecision(state) and agentId == currentAgentId:
		# trading is done for all agents in this turn
		return Phase.BUY

	if nextAgentId == currentAgentId:
		# trading is done for all agents in this turn
		if context.auctionStarted:
			return Phase.AUCTION
		return Phase.BUY_HOUSES
	
	# do mortgage, selling and trade for the next agent
	return Phase.MORTGAGE

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

"""
Property may be Get Out of Jail Free cards (propertyId = 40,41)
The property being traded and other properties in the same color group
can't have houses/hotels on them.
"""
def validPropertyToTrade(context,playerId, propertyId):
	state = context.state
	propertyId = typecast(propertyId,int,-1)
	if propertyId<0 or propertyId>BOARD_SIZE+1:
		return False
	if not state.rightOwner(playerId,propertyId):
		return False
	if propertyId > BOARD_SIZE-1:
		return True
	if board[propertyId]['class']=="Railroad" or board[propertyId]['class']=="Utility":
		return True
	if board[propertyId]['class']!="Street":
		return False
	if state.getNumberOfHouses(propertyId) > 0:
		return False
	for monopolyElement in board[propertyId]['monopoly_group_elements']:
		if state.getNumberOfHouses(monopolyElement) > 0:
			return False
	return True

"""Checks if a proposed trade is valid"""
def validateTradeAction(context,agentId,action):
	if not isinstance(action, list) and not isinstance(action, tuple):
		return False
	if len(action) != 5:
		return False
	otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = action
	state = context.state
	passed = False
	if otherAgentId == agentId:
		return False
	for playerId in state.getLivePlayers():
		if otherAgentId == playerId:
			passed = True
			break
	if not passed:
		return False
	
	cashOffer = check_valid_cash(cashOffer)
	cashRequest = check_valid_cash(cashRequest)
	currentPlayerCash = state.getCash(agentId)
	otherPlayerCash = state.getCash(otherAgentId)
	if cashOffer > currentPlayerCash:
		return False
	if cashRequest > otherPlayerCash:
		return False
	
	if not isinstance(propertiesOffer, list) and not isinstance(propertiesOffer, tuple):
			return False
	for propertyId in propertiesOffer:
		if not validPropertyToTrade(context, agentId, propertyId):
			return False

	if not isinstance(propertiesRequest, list) and not isinstance(propertiesRequest, tuple):
			return False
	for propertyId in propertiesRequest:
		if not validPropertyToTrade(context, otherAgentId, propertyId):
			return False
	
	return True
