from utils import typecast
from constants import board
from state import Phase
from config import log
from actions.constants import MAX_TRADES

def publish(context):
	# will not be bankrupt if we reach here
	agentId = context.tradeReceiver

	log("game","Agent {} has been asked for a trade response!".format(agentId))
	
	return [agentId]
	
def subscribe(context,responses):
	state = context.state
	agentId,tradeResponse = list(responses.items())[0]

	tradeResponse = typecast(tradeResponse, bool, False)
	if tradeResponse:
		processTradeSuccess(context,agentId)
	else:
		log("game","Agent {} refused trade offer from {}!".format(agentId,state.getPhasePayload()[0]))
	
	otherAgentId = state.getPhasePayload()[0]
	state.setPhasePayload(None)
	context.tradeCounter+=1
	if context.tradeCounter < MAX_TRADES:
		# continue trades for the same agent
		return Phase.TRADE

	noPlayers = len(context.state.players)
	nextIndex = (state.getPlayerIndex(otherAgentId) + 1) % noPlayers
	nextAgentId = state.getPlayerId(nextIndex)
	currentAgentId = state.getCurrentPlayerId()
	context.bsmAgentId = nextAgentId

	# resetting trade counter for other agents
	context.tradeCounter = 0

	if isBuyDecision(state) and otherAgentId == currentAgentId:
		# trading is done for all agents in this turn
		return Phase.BUY

	if nextAgentId == currentAgentId:
		# trading is done for all agents in this turn
		if context.auctionStarted:
			return Phase.AUCTION
		return Phase.UNMORTGAGE
	
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

def processTradeSuccess(context,agentId):
	state = context.state
	# here, otherAgentId is the player who proposed the trade
	otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = state.getPhasePayload()
	
	# trade could be to escape debt where we need to clear debt accordingly
	# if cashRequest is greater, it means agentId should pay the difference to otherAgentId
	if cashRequest > cashOffer:
		state.addDebt(agentId,cashRequest - cashOffer,otherAgentId)
	else:
		state.addDebt(otherAgentId,cashOffer - cashRequest,agentId)

	for propertyRequest in propertiesRequest:
		state.setPropertyOwner(propertyRequest,otherAgentId)
	for propertyOffer in propertiesOffer:
		state.setPropertyOwner(propertyOffer,agentId)
			
	# Handle mortgaged properties that were involved in the trade after transferring ownership
	mortgagedProperties = list(filter(lambda propertyId : state.isPropertyMortgaged(propertyId), propertiesOffer + propertiesRequest))
	for mortgagedProperty in mortgagedProperties:
		if mortgagedProperty in context.mortgagedDuringTrade:
			continue
		
		context.mortgagedDuringTrade.append(mortgagedProperty)
		propertyPrice = board[mortgagedProperty]['price']
		mortgagedPrice = int(propertyPrice/2)
		agentInQuestion = state.getPropertyOwner(mortgagedProperty)

		# TODO: could this be done better?
		# We're not checking in handleTrade if the agent has enough cash
		# when a mortgaged property is traded, the new owner needs to pay
		# its interest immediately to the bank
		state.addDebt(agentInQuestion,int(mortgagedPrice*0.1))

	log("game","Trade request from agent {} to {} was a success!".format(otherAgentId,agentId))
