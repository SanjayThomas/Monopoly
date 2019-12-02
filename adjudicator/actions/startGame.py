from config import log
from dice import Dice
from cards import Cards
from state import State, Phase, Property, NUMBER_OF_PROPERTIES
from constants import communityChestCards, chanceCards

# should return the agents for which publish API must be called in mapper
# we don't check agentOptions here because this call is mandatory
def publish(context):
	#reinitialize state for the new game
	context.winner = None
	context.dice = Dice()
	context.chest = Cards(communityChestCards)
	context.chance = Cards(chanceCards)
	
	if context.INITIAL_STATE == "DEFAULT":
		context.state =  State(context.state.players)
	elif context.INITIAL_STATE == "TEST_BUY_HOUSES":
		properties = [Property(0,False,False,0,i) for i in range(NUMBER_OF_PROPERTIES)]
		agentOne = context.state.players[0]
		properties[6].ownerId = agentOne
		properties[8].ownerId = agentOne
		properties[9].ownerId = agentOne
		agentTwo = context.state.players[1]
		properties[11].ownerId = agentTwo
		properties[13].ownerId = agentTwo
		properties[14].ownerId = agentTwo
		context.state = State(context.state.players,properties)
		
	log("game","Game #"+str(context.gamesCompleted+1)+" started.")
	
	# all the agents provided can access the startGame API
	return context.state.players

# should return the phase that follows the current one
def subscribe(context, responses):
	return Phase.START_TURN
