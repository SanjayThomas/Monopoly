from config import log
from state import Phase
from actions.constants import JAIL, JUST_VISTING, CHANCE_GET_OUT_OF_JAIL_FREE, COMMUNITY_GET_OUT_OF_JAIL_FREE
from constants import communityChestCards, chanceCards

# only called for one agent
def publish(context):
	# This is the action class from where the turn would start on rolling a double.
	# Basically, if the turn is legitimate, the game has to pass through here.
	context.mortgagedDuringTrade = []
	
	state = context.state
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	if playerPosition != JAIL:
		#player is not in jail.
		#send the player directly to diceRoll
		log("game","Agent {} is not in Jail.".format(currentPlayerId))
		return []
	
	log("game","Agent {} is in Jail.".format(currentPlayerId))
	state.setPhasePayload(None)
	return [currentPlayerId]

def subscribe(context, responses):
	currentPlayerId,response = list(responses.items())[0]

	playerPosition = context.state.getPosition(currentPlayerId)
	if playerPosition != JAIL:
		context.diceThrown = False
		return Phase.DICE_ROLL

	# agent is currently in jail
	outOfJail,diceThrown = handle_in_jail_state(context.state,response)

	context.diceThrown = diceThrown
	
	# TODO: next phase should be JAIL_RESULT
	#let the player know if he is out of jail or not
	# state.setPhasePayload(outOfJail)
	
	if outOfJail:
		return Phase.DICE_ROLL

	return Phase.END_TURN

"""
Incoming action format:
("R",) : represents rolling to get out
("P",) : represents paying $50 to get out (BSMT should follow)
("C", propertyNumber) : represents using a get out of jail card.
Return values are 2 boolean values:
1. Whether the player is out of jail.
2. Whether there was a dice throw while handling jail state.
"""
def handle_in_jail_state(state,action):
	currentPlayerId = state.getCurrentPlayerId()
	
	log("game","Agent {}'s Jail Decision: {}".format(currentPlayerId,action))

	if action=="R" or action=="P":
		action = (action,)
	
	if (isinstance(action, tuple) or isinstance(action, list)) and len(action)>0:
		if action[0] == 'P':
			playerCash = state.getCash(currentPlayerId)
			# TODO: The player may not have enough money here. Is this the correct way to implement this?
			if playerCash>=50:
				state.setCash(currentPlayerId,playerCash-50)
			else:
				state.addDebt(currentPlayerId,50)
			
			state.setPosition(currentPlayerId,JUST_VISTING)
			state.resetJailCounter(currentPlayerId)
			return [True,False]
		
		elif action[0] == 'C':
			#Check if the player has the mentioned property card.
			if (len(action)>1) & (action[1] in [CHANCE_GET_OUT_OF_JAIL_FREE,COMMUNITY_GET_OUT_OF_JAIL_FREE]):
				
				if state.rightOwner(currentPlayerId,action[1]):
					if action[1] == COMMUNITY_GET_OUT_OF_JAIL_FREE:
						chest.deck.append(communityChestCards[4])
					elif action[1] == CHANCE_GET_OUT_OF_JAIL_FREE:
						chance.deck.append(chanceCards[7])
					
					state.setPropertyUnowned(action[1])
					
					state.setPosition(currentPlayerId,JUST_VISTING)
					state.resetJailCounter(currentPlayerId)
					return [True,False]
	
	"""If both the above method fail for some reason, we default to dice roll."""
	dice.roll()
	if dice.double:
		# Player can go out
		# Need to ensure that there is no second turn for the player in this turn.
		dice.double = False
		dice.double_counter = 0
		state.setPosition(currentPlayerId,JUST_VISTING)
		state.resetJailCounter(currentPlayerId)
		return [True,True]
	
	state.incrementJailCounter(currentPlayerId)
	if state.getJailCounter(currentPlayerId)==3:
		playerCash = state.getCash(currentPlayerId)
		#The player has to pay $50 and get out. 
		if playerCash>=50:
			state.setCash(currentPlayerId,playerCash-50)
		else:
			#This is added as debt so that the player has the opportunity to resolve it.
			state.addDebt(currentPlayerId,50)
		state.setPosition(currentPlayerId,JUST_VISTING)
		state.resetJailCounter(currentPlayerId)

		log("jail","Agent {} has been in jail for 3 turns. Forcing him to pay $50 to get out.".format(currentPlayerId))
		return [True,True]
	return [False,True]
