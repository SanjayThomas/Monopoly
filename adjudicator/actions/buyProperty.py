from config import log
from utils import typecast
from state import Phase
from constants import board

# landed on an unowned property. Buy or Auction?
# if the agent doesn't have the cash to buy the property, send straight to auction
def publish(context):
	state = context.state
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	playerCash = state.getCash(currentPlayerId)
	price = board[playerPosition]['price']
	
	state.setPhasePayload(playerPosition)
	
	log("buy","Agent {} has landed on the unowned property {}".format(currentPlayerId, playerPosition))

	if price > playerCash:
		# default to auction
		return []

	return [currentPlayerId]

def subscribe(context, responses):
	currentPlayerId,response = list(responses.items())[0]
	response = typecast(response, bool, False)

	if response:
		handle_buy_property(context.state)
	else:
		context.auctionStarted = True
		
	return Phase.MORTGAGE

def handle_buy_property(state):
	"""
	Handle the action response from the Agent for buying an unowned property
	Only called for the currentPlayer during his turn.
	"""
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	playerCash = state.getCash(currentPlayerId)
	space = board[playerPosition]

	# if we reach here, player is assured to have the money required
	state.setPropertyOwner(playerPosition,currentPlayerId)
	state.setCash(currentPlayerId,playerCash-space['price'])
	state.setPhasePayload(None)
	log('buy',"Agent {} has bought {}".format(currentPlayerId,space['name']))
