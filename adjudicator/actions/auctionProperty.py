from config import log
from state import Phase
from utils import check_valid_cash

# broadcast call to all live players
def publish(context):
	state = context.state
	context.auctionStarted = False
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	state.setPhasePayload(playerPosition)
	
	log("auction","Agent {} has decided to auction the property {}".format(currentPlayerId,state.getPhasePayload()))
	
	return list(state.getLivePlayers())

def subscribe(context,reponses):
	state = context.state

	# the current player wins by default for bid of $1
	auctionWinner = state.getCurrentPlayerId()
	winningBid = 1

	for agentId,bid in reponses.items():
		playerCash = state.getCash(agentId)
		playerDebt = state.getDebt(agentId)
		bid = check_valid_cash(bid)

		#Only if the player has enough money should his bid be considered valid
		# TODO: bids could be the same
		if bid > winningBid and (playerCash - playerDebt) >= bid:
			auctionWinner = agentId
			winningBid = bid

	auctionedProperty = state.getPhasePayload()
	playerCash = state.getCash(auctionWinner)
	playerCash -= winningBid
	state.setCash(auctionWinner,playerCash)
	state.setPropertyOwner(auctionedProperty,auctionWinner)
	log("auction","Agent {} won the Auction with a bid of {}".format(auctionWinner,winningBid))

	# phasePayload = [auctionedProperty,auctionWinner,winningBid]
	# state.setPhasePayload(phasePayload)
	# return Phase.AUCTION_RESULT
	
	state.setPhasePayload(None)
	return Phase.BUY_HOUSES
