import random
from collections import namedtuple
import json

from board import board, MAX_HOUSES, MAX_HOTELS, groups, Group

StateTuple = namedtuple("StateTuple", "current_player turn properties positions money phase phaseData")
TradeData = namedtuple("TradeData", "moneyOffered propertiesOffered moneyRequested propertiesRequested")


# makes it possible to print a state without printing all of the past states
class StateList(list):
    def __str__(self):
        return str(len(self)) + " past states"

    def __repr__(self):
        return str(len(self)) + " past states"

    def __deepcopy__(self, memo):
        return StateList(self)


class Property:
    def __init__(self, id, owner, houses, mortgaged):
        self.id = id
        self.data = board[id] if id < 40 else None
        self.owner = owner
        # 5 houses = hotel
        self.houses = houses
        self.mortgaged = mortgaged

    def __str__(self):
        return str(self.id) + "," + str(self.owner) + "," + str(self.houses) + "," + str(self.mortgaged)

    # speed up deepcopy of state
    def __deepcopy__(self, memo):
        return Property(self.id, self.owner, self.houses, self.mortgaged)


class State:
    def __init__(self, stateTuple):
        if stateTuple:
            stateTuple = json.loads(stateTuple)
            self.player_ids = stateTuple['player_ids']
            self.current_player_id = stateTuple['current_player_id']
            self.turn = stateTuple['turn_number']
            self.properties = []
            for id, value in enumerate(stateTuple['properties']):
                owner = value['ownerId']
                mortgaged = value['mortgaged']
                houses = value['houses']
                self.properties.append(Property(id, owner, houses, mortgaged))

            self.positions = stateTuple['player_board_positions']
            self.money = stateTuple['player_cash']
            self.bankrupt = stateTuple['player_loss_status']
            self.phase = stateTuple['phase']
            self.phaseData = stateTuple['phase_payload']

    def getOpponents(self, id):
        return [playerId for playerId in self.player_ids if not playerId == id]

    def getNextRoll(self):
        if self.diceRolls:
            return self.diceRolls.pop(0)
        if self.diceRolls == []:
            raise GameOverException
        return random.randint(1, 6), random.randint(1, 6)

    def getHousesRemaining(self):
        houses = MAX_HOUSES
        for prop in self.properties:
            if prop.houses < 5: houses -= prop.houses
        return houses

    def getHotelsRemaining(self):
        hotels = MAX_HOTELS
        for prop in self.properties:
            if prop.houses == 5: hotels -= 1
        return hotels

    def getGroupProperties(self, group):
        if group < 0 or group >= len(groups):
            # invalid index
            return []
        return [self.properties[id] for id in groups[group]]

    def getOwnedProperties(self, player):
        return [prop for prop in self.properties if prop.owner == player and prop.id < 40]

    def getOwnedGroupProperties(self, player):
        owned = self.getOwnedProperties(player)
        return [prop for prop in owned if self.playerOwnsGroup(player, prop.data.group)]

    def getOwnedGroups(self, player):
        return [group for group in range(0, 10) if self.playerOwnsGroup(player, group)]

    def getOwnedBuildableGroups(self, player):
        return [group for group in range(0, 8) if self.playerOwnsGroup(player, group)]

    def playerOwnsGroup(self, player, group):
        for prop in self.getGroupProperties(group):
            if not prop.owner == player: return False
        return True

    def getRailroadCount(self, player):
        count = 0
        for prop in self.getGroupProperties(Group.RAILROAD):
            if prop.owner == player: count += 1
        return count

    def toTuple(self):
        return StateTuple(self.current_player_id, self.turn, [str(prop) for prop in self.properties], self.positions,
                          self.money, self.phase, self.phaseData)

    def __str__(self):
        return str(self.toTuple())


class Phase:
    START_GAME = 'START_GAME'
    START_TURN = 'START_TURN'
    JAIL = 'JAIL'
    DICE_ROLL = 'DICE_ROLL'
    CHANCE_CARD = 'CHANCE_CARD'
    COMMUNITY_CHEST = 'COMMUNITY_CHEST'
    MORTGAGE = 'MORTGAGE'
    SELL_HOUSES = 'SELL_HOUSES'
    BUY = 'BUY'
    BUY_RESULT = 'BUY_RESULT'
    AUCTION = 'AUCTION'
    TRADE = 'TRADE'
    TRADE_RESPONSE = 'TRADE_RESPONSE'
    BUY_HOUSES = 'BUY_HOUSES'
    END_TURN = 'END_TURN'
    END_GAME = 'END_GAME'


class GameOverException(Exception):
    pass
