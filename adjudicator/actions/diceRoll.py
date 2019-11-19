from config import log
from constants import board
from actions.constants import JAIL, BOARD_SIZE, PASSING_GO_MONEY
from state import Phase
from constants import board

# TODO: should this be broadcast?
def publish(context):
	state = context.state
	dice = context.dice
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	playerCash = state.getCash(currentPlayerId)
	
	log("game","Agent {} about to throw dice.".format(currentPlayerId))
	
	if not context.diceThrown:
		# TODO: Debug dice
		dice.roll()
	
	if dice.double_counter == 3:
		# send player to END_TURN
		send_player_to_jail(context.state,dice)
	else:
		#Update player position
		playerPosition += (dice.die_1 + dice.die_2)
		
		#Passing Go
		if playerPosition>=BOARD_SIZE:
			playerPosition = playerPosition % BOARD_SIZE
			playerCash += PASSING_GO_MONEY
		
		state.setCash(currentPlayerId,playerCash)
		state.setPosition(currentPlayerId,playerPosition)
	
	currentPhase = state.getPhase()
	agentOptions = context.agents[currentPlayerId]['agentOptions']
	shouldPublish = agentOptions.get(currentPhase, True)
	if not shouldPublish:
		return []

	# let the agent know whether he is in Jail
	# if not, let him know his new position after dice roll
	state.setPhasePayload([dice.die_1, dice.die_2])
	return [currentPlayerId]

def subscribe(context,responses):
	context.bsmAgentId = list(responses.keys())[0]
	context.state.setPhasePayload(None)
	return determine_position_effect(context.state,context.dice)

"""
Performed after dice is rolled and the player is moved to a new position.
Determines the effect of the position and action required from the player.
"""	 
def determine_position_effect(state,dice):
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	playerCash = state.getCash(currentPlayerId)
	propertyClass = board[playerPosition]['class']
	
	if propertyClass == 'Street' or propertyClass == 'Railroad' or propertyClass == 'Utility':
		isPropertyOwned = state.isPropertyOwned(playerPosition)
		isRightOwner = state.rightOwner(currentPlayerId,playerPosition)
		isPropertyMortgaged = state.isPropertyMortgaged(playerPosition)
		
		if isPropertyOwned and not isRightOwner and not isPropertyMortgaged:
			rent = calculateRent(state,dice)
			state.addDebt(currentPlayerId,rent)
		
		return Phase.MORTGAGE
		
	elif (propertyClass == 'Chance'):
		return Phase.CHANCE_CARD
	elif (propertyClass == 'Chest'):
		return Phase.COMMUNITY_CHEST
	elif propertyClass == 'Tax':
		tax = board[playerPosition]['tax']
		state.addDebt(currentPlayerId,tax)
		return Phase.MORTGAGE
	elif propertyClass == 'GoToJail':
		send_player_to_jail(state,dice)
		return Phase.END_TURN
	elif propertyClass == 'Jail':
		# if player is jail, should they get BSM?
		# need to make sure player sent to jail in publish doesn't get BSM then
		return Phase.END_TURN
	
	#Represents Go,Jail(Visiting),Free Parking
	return Phase.MORTGAGE

def send_player_to_jail(state,dice):
	currentPlayerId = state.getCurrentPlayerId()
	
	log("jail","Agent {} has been sent to jail".format(currentPlayerId))

	# send the player to jail and end the turn
	# Disable double
	dice.double = False
	dice.double_counter = 0
	state.setPosition(currentPlayerId,JAIL)
	state.setPhasePayload(None)

# Property is not owned by current player. Calculate the rent he has to pay.
def calculateRent(state,dice):
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	ownerId = state.getPropertyOwner(playerPosition)
	
	space = board[playerPosition]
	monopolies = space['monopoly_group_elements']
	counter = 0
	for monopoly in monopolies:
		if state.rightOwner(ownerId,monopoly):
			counter += 1
	
	if (space['class'] == 'Street'):
		houseCount = state.getNumberOfHouses(playerPosition)
		rent = space['rent'][houseCount]
		if counter==len(monopolies) and houseCount==0:
			rent = rent * 2
	
	elif (space['class'] == 'Railroad'):
		rent = space['rent'][counter]
	elif (space['class'] == 'Utility'):
		rent = space['rent'][counter]
		rent = rent * (dice.die_1 + dice.die_2)
	
	return rent
