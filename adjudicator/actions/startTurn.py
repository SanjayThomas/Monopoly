from config import log
from state import Phase
from actions.constants import TOTAL_NO_OF_TURNS

def publish(context):
	state = context.state

	#turnNo starts from -1
	if state.getTurn()+1 >= TOTAL_NO_OF_TURNS:
		#skip this turn.
		return []

	state.updateTurn()
	log("turn","Turn {} start".format(state.getTurn()))
	
	agentId = state.getCurrentPlayerId()
	if state.hasPlayerLost(agentId):
		#skip this turn.
		return []

	context.dice.reset()

	currentPhase = state.getPhase()
	agentOptions = context.agents[agentId]['agentOptions']
	shouldPublish = agentOptions.get(currentPhase, True)
	if not shouldPublish:
		return []
	
	return [agentId]

def subscribe(context, responses):
	state = context.state
	agentId = list(responses.keys())[0]

	if (state.getTurn()+1 >= TOTAL_NO_OF_TURNS) or (state.hasPlayerLost(agentId)):
		return Phase.END_TURN
	
	return Phase.JAIL
