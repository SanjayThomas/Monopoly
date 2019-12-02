from config import log
from constants import board
from actions.constants import JAIL,BOARD_SIZE,PASSING_GO_MONEY,CHANCE_GET_OUT_OF_JAIL_FREE,COMMUNITY_GET_OUT_OF_JAIL_FREE
from state import Phase
from constants import board,communityChestCards,chanceCards

# only to current agent
def publish(context):
	state = context.state
	currentPlayerId = state.getCurrentPlayerId()
	currentPhase = state.getPhase()

	if currentPhase == Phase.CHANCE_CARD:
		card = context.chance.draw_card()
	else:
		card = context.chest.draw_card()
	
	state.setPhasePayload(card['id'])
	
	agentOptions = context.agents[currentPlayerId]['agentOptions']
	shouldPublish = agentOptions.get(currentPhase, True)
	if not shouldPublish:
		return []

	return [currentPlayerId]

def subscribe(context,responses):
	state = context.state
	agentId = list(responses.keys())[0]
	cardId = state.getPhasePayload()
	if state.getPhase() == Phase.CHANCE_CARD:
		card = chanceCards[cardId]
		deck = "chance"
	else:
		card = communityChestCards[cardId]
		deck = "chest"

	log('game','Agent {} has drawn the {} card: {}'.format(agentId,deck,cardId))

	state.setPhasePayload(None)
	return handle_cards_pre_turn(context,card,deck)

"""Method handles various events for Chance and Community cards"""
def handle_cards_pre_turn(context,card,deck):
	state = context.state
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	updateState = False
	
	if card['type'] == 1:
		# -ve means you need to pay
		if card['money']<0:
			state.addDebt(currentPlayerId,abs(card['money']))
		else:
			state.addCash(currentPlayerId,abs(card['money']))

	elif card['type'] == 2:
		#-ve represents you need to pay
		for playerId in state.getLivePlayers():
			if playerId!=currentPlayerId:
				if card['money']<0:
					# TODO: not sure how to handle case where currentPlayerId goes bankrupt with debt against multiple players
					# temp workaround: pay the other agents and add debt as from bank for currentPlayerId
					state.addCash(playerId,abs(card['money']))
					state.addDebt(currentPlayerId,abs(card['money']))
				else:
					state.addDebt(playerId,abs(card['money']),currentPlayerId)
		
	elif card['type'] == 3:
		if card['position'] == JAIL:
			#sending the player to jail
			return send_player_to_jail(state,context.dice)
		
		if (card['position'] - 1) < playerPosition:
			#Passes Go
			state.addCash(currentPlayerId,PASSING_GO_MONEY)
		playerPosition = card['position'] - 1
		updateState = True
			
	elif card['type'] == 4:
		"""Get out of Jail free"""
		if deck == 'Chest':
			propertyValue = COMMUNITY_GET_OUT_OF_JAIL_FREE
		else:
			propertyValue = CHANCE_GET_OUT_OF_JAIL_FREE
		
		state.setPropertyOwner(propertyValue,currentPlayerId)
	
	elif card['type'] == 5:
		n_houses = 0
		n_hotels = 0
		for p in state.properties:
			if state.rightOwner(currentPlayerId, p.propertyId):
				housesCount = state.getNumberOfHouses(p.propertyId)
				if housesCount==5:
					n_hotels+=1
				else:
					n_houses+=housesCount

		debt = abs(card['money'])*n_houses + abs(card['money2'])*n_hotels
		state.addDebt(currentPlayerId,debt)
	
	elif card['type'] == 6:
		#Advance to nearest railroad. Pay 2x amount if owned
		if (playerPosition < 5) or (playerPosition>=35):
			if (playerPosition>=35):
				#Passes Go
				state.addCash(currentPlayerId,PASSING_GO_MONEY)
			playerPosition = 5
		elif (playerPosition < 15) and (playerPosition>=5):
			playerPosition = 15
		elif (playerPosition < 25) and (playerPosition>=15):
			playerPosition = 25
		elif (playerPosition < 35) and (playerPosition>=25):
			playerPosition = 35
		
		updateState = True
	
	elif card['type'] == 7:
		#Advance to nearest utility. Pay 10x dice roll if owned
		if (playerPosition < 12) or (playerPosition>=28):
			if (playerPosition>=28):
				#Passes Go
				state.addCash(currentPlayerId,PASSING_GO_MONEY)
			playerPosition = 12
		elif (playerPosition < 28) and (playerPosition>=12):
			playerPosition = 28
		
		ownerId = state.getPropertyOwner(playerPosition)
		isPropertyMortgaged = state.isPropertyMortgaged(playerPosition)
		if (ownerId != currentPlayerId) and not isPropertyMortgaged:
			#Check if owned by opponent
			#TODO: Debug dice
			context.dice.roll(ignore=True)
			state.addDebt(currentPlayerId,10 * (context.dice.die_1 + context.dice.die_2),ownerId)
	
	elif card['type'] == 8:
		#Go back 3 spaces
		playerPosition -= 3 
		updateState = True
	else:
		log('game','Invalid card type {type}...'.format(type=card['type']))
	
	# playerPosition != JAIL
	state.setPosition(currentPlayerId,playerPosition)

	if not updateState:
		return Phase.MORTGAGE

	return determine_position_effect(state,context.dice)

"""
Performed after dice is rolled and the player is moved to a new position.
Determines the effect of the position and action required from the player.
"""	 
def determine_position_effect(state,dice):
	currentPlayerId = state.getCurrentPlayerId()
	playerPosition = state.getPosition(currentPlayerId)
	propertyClass = board[playerPosition]['class']
	
	if propertyClass == 'Street' or propertyClass == 'Railroad' or propertyClass == 'Utility':
		ownerId = state.getPropertyOwner(playerPosition)
		isPropertyMortgaged = state.isPropertyMortgaged(playerPosition)
		
		if (ownerId != currentPlayerId) and not isPropertyMortgaged:
			rent = calculateRent(state,dice)
			state.addDebt(currentPlayerId,rent,ownerId)
		
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
		return send_player_to_jail(state,dice)
	
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
	return Phase.END_TURN

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
