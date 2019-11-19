from config import log
from state import Phase
from constants import board
from actions.constants import TOTAL_NO_OF_TURNS

# called for only one agent
def publish(context):
	state = context.state
	handle_payment(context)
	
	lossCount = 0
	for agentId in context.PLAY_ORDER:
		if state.hasPlayerLost(agentId): lossCount+=1
	
	TOTAL_NO_OF_PLAYERS = len(context.PLAY_ORDER)
	if (lossCount>=TOTAL_NO_OF_PLAYERS-1) or (state.getTurn()+1 >= TOTAL_NO_OF_TURNS):
		#Only one player left or last turn is completed. Winner can be decided.
		log("turn","Turn {} end".format(state.getTurn()))
		return []
	else :
		if not context.dice.double:
			log("turn","Turn {} end".format(state.getTurn()))
			return [state.getCurrentPlayerId()]
		else:
			# go to JailDecision instead
			log("turn","Double had been rolled.")
			return []

def subscribe(context, responses):
	state = context.state
	agentId = list(responses.keys())[0]

	lossCount = 0
	for agentId in context.PLAY_ORDER:
		if state.hasPlayerLost(agentId): lossCount+=1

	TOTAL_NO_OF_PLAYERS = len(context.PLAY_ORDER)
	if (lossCount>=TOTAL_NO_OF_PLAYERS-1) or (state.getTurn()+1 >= TOTAL_NO_OF_TURNS):
		return Phase.END_GAME
	else:
		#TODO: should this be cleared?
		if context.dice.double and not state.hasPlayerLost(agentId):
			return Phase.JAIL
		else:
			return Phase.START_TURN

"""
Handling payments the player has to make to the bank/opponent
Could be invoked for either player during any given turn.
Returns 2 boolean list - True if the player was able to pay off his debt
"""
def handle_payment(context):
	for playerId in context.PLAY_ORDER:
		if not context.state.hasPlayerLost(playerId):
			context.state.clearDebt(playerId)
	