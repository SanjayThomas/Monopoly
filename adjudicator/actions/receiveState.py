from config import log
from state import Phase
from constants import board

# called for all RESULT phases
# these phases are simply to let the agents know whether the previous action
# was successful or not
def publish(context):
	state = context.state
	return context.state.players

def subscribe(context, responses):
	state = context.state
	payload = state.getPhasePayload()
	context.state.setPhasePayload(None)
	currentPhase = state.getPhase()

	if currentPhase == Phase.AUCTION_RESULT:
		return Phase.UNMORTGAGE
	if currentPhase == Phase.MORTGAGE_RESULT:
		return Phase.SELL_HOUSES
	if currentPhase == Phase.SELL_HOUSES_RESULT:
		return Phase.TRADE
	if currentPhase == TRADE_RESULT:
		pass
	if currentPhase == Phase.BUY_HOUSES_RESULT:
		currentAgentId = state.getCurrentPlayerId()
		if context.bsmAgentId == currentAgentId:
			return Phase.END_TURN
		return Phase.UNMORTGAGE
	if currentPhase == Phase.BUY_RESULT:
		return Phase.MORTGAGE
	if currentPhase == Phase.JAIL_RESULT:
		if payload:
			return Phase.DICE_ROLL
		return Phase.END_TURN
	if currentPhase == Phase.UNMORTGAGE_RESULT:
		return Phase.BUY_HOUSES
