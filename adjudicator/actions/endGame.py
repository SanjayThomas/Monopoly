from config import log
from constants import board
from state import Phase
from actions.constants import BOARD_SIZE,CHANCE_GET_OUT_OF_JAIL_FREE,COMMUNITY_GET_OUT_OF_JAIL_FREE
from math import ceil
from functools import partial
from twisted.internet import reactor

def publish(context):
    log("game","Game #{} has ended.".format(context.gamesCompleted+1))
    
    resultsArray = final_winning_condition(context)
    log("win","Agents {} won the Game.".format(resultsArray))
    
    winners = resultsArray
    for winner in winners:
        context.agents[winner]['wins']+=1
    #Allow the agent to make changes based on current game results
    context.gamesCompleted+=1

    context.uiUpdateChannel({'type':0,'winners':winners})
    
    if context.gamesCompleted < context.noGames:
        context.state.setPhasePayload(winners)
    else:
        #All the games have completed
        winCount = {}
        for agentId,data in context.agents.items():
            winCount[agentId] = data['wins']
        context.state.setPhasePayload(winCount)

    return context.PLAY_ORDER

def subscribe(context,responses):
    if context.gamesCompleted < context.noGames:
        #Start the next game
        context.state.setPhasePayload(None)

        # ceil should ensure shuffleFactor > 0
        shuffleFactor = ceil(context.noGames/context.noPlayers)
        if context.gamesCompleted % shuffleFactor == 0:
            context.PLAY_ORDER.append(context.PLAY_ORDER.pop(0))

        return Phase.START_GAME
    
    # game has ended
    return None

"""
On final winner calculation, following are considered:
Player's cash,
Property value as on the title card,
House and Hotel purchase value,
Mortgaged properties at half price.
"""
def final_winning_condition(context):
    agentCash = {}
    agentPropertyWorth = {}
    state = context.state
    
    for playerId in context.PLAY_ORDER:
        agentCash[playerId] = state.getCash(playerId)
        agentPropertyWorth[playerId] = 0
    
    for propertyId in range(BOARD_SIZE):
        # In 0 to 39 board position range
        isPropertyOwned = state.isPropertyOwned(propertyId)
        ownerId = state.getPropertyOwner(propertyId)
        houses = state.getNumberOfHouses(propertyId)
        mortgaged = state.isPropertyMortgaged(propertyId)
        
        price = board[propertyId]['price']
        build_cost = board[propertyId]['build_cost']
        
        if isPropertyOwned:
            if mortgaged:
                agentPropertyWorth[ownerId] += int(price/2)
            else:
                agentPropertyWorth[ownerId] += (price+build_cost*houses)
    
    for propertyId in [CHANCE_GET_OUT_OF_JAIL_FREE,COMMUNITY_GET_OUT_OF_JAIL_FREE]:
        isPropertyOwned = state.isPropertyOwned(propertyId)
        ownerId = state.getPropertyOwner(propertyId)
        if isPropertyOwned:
            agentPropertyWorth[ownerId] += 50
    
    #Using an array here to handle ties
    winners = []
    highestAssets = 0
    for playerId in context.PLAY_ORDER:
        turn_of_loss = state.getTurnOfLoss(playerId)
        if turn_of_loss==-1:
            log("win_condition","Agent {} Cash: {}".format(playerId,agentCash[playerId]))
            log("win_condition","Agent {} Property Value: {}".format(playerId,agentPropertyWorth[playerId]))
            playerAssets = agentCash[playerId]+agentPropertyWorth[playerId]
            if playerAssets > highestAssets:
                winners = [playerId]
                highestAssets = playerAssets
            elif playerAssets == highestAssets:
                winners.append(playerId)
        else:
            log("win_condition","Agent {} had lost in the turn: {}".format(playerId,turn_of_loss))

    # very rare occurence where multiple people lost in last turn
    if len(winners) == 0:
        highestTurnOfLoss = -1
        for playerId in context.PLAY_ORDER:
            turn_of_loss = state.getTurnOfLoss(playerId)
            if turn_of_loss > highestTurnOfLoss:
                highestTurnOfLoss = turn_of_loss
                winners = [playerId]
            elif turn_of_loss == highestTurnOfLoss:
                winners.append(playerId) 
    
    return winners
