from config import log
from state import Phase
from constants import board
from actions.constants import TOTAL_NO_OF_TURNS

# called for only one agent
def publish(context):
	state = context.state
	state.clearDebts()
	
	lossCount = 0
	for agentId in context.state.players:
		if state.hasPlayerLost(agentId): lossCount+=1
	
	if (lossCount>=len(context.state.players)-1) or (state.getTurn()+1 >= TOTAL_NO_OF_TURNS):
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
	for agentId in context.state.players:
		if state.hasPlayerLost(agentId): lossCount+=1

	if (lossCount>=len(context.state.players)-1) or (state.getTurn()+1 >= TOTAL_NO_OF_TURNS):
		return Phase.END_GAME
	else:
		#TODO: should this be cleared?
		if context.dice.double and not state.hasPlayerLost(agentId):
			return Phase.JAIL
		else:
			return Phase.START_TURN
