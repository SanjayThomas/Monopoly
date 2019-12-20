import sys
import json
from os import environ
from board import Type, Group
from state import State
from baseAgent import BaseAgent

import six
from autobahn.twisted.wamp import ApplicationRunner

import csv, uuid


# fill in your code here
# for details about the API spec, refer here:
# https://docs.google.com/document/d/1LdlJH4ZXY9QQZKpb_5BizeE5k9vOUkQKY_cEdxky-5I/edit?usp=sharing
class GOATAgent(BaseAgent):
    def startGame(self, state):
	# each "game" is a actually a series of games run in succession.
	# this function can be used for initial setup before each such game.  
	# TODO: your code here
	return None

    def mortgage(self, state):
	# state is a JSON encoded string containing the game state
	stateTuple = json.loads(state)
	#stateTuple['player_ids'] # ID's of all the agents in this game
	#stateTuple['current_player_id'] # your agent's ID
	#stateTuple['turn_number'] # integer turn number
	#stateTuple['properties'] # array of properties on the monopoly board
	# each element of the properties array is a 3 element tuple containing the values for:
	# ownerId,mortgaged,houses
	#stateTuple['player_board_positions'] # position of all players on the board
	#stateTuple['player_cash'] # the cash each player has in hand
	#stateTuple['player_loss_status'] # boolean array stating whether a player has gone bankrupt (True = Bankrupt)
	#stateTuple['phase'] # the game proceeds as a sequence of Phases, this String identifies the current Phase
	#stateTuple['phase_payload'] # Some phases could have special data that needs to be conveyed to the user.
	# for eg, if your agent is asked for a trade response, the phase payload would be:
	#[<requesting agent's ID>,<cash offered>,<properties offered>,<cash requested>,<properties requested>]
	
        # TODO: your code here
        return None

    def unmortgage(self, state):
        # TODO: your code here
        return None

    def sellHouses(self, state):
        # TODO: your code here
        return None

    def buyHouses(self, state):
        # TODO: your code here
        return None

    def respondTrade(self, state):
        # TODO: your code here
        return False

    def buyProperty(self, state):
        # TODO: your code here
        return True

    def auctionProperty(self, state):
        # TODO: your code here
        return 1

    def jailDecision(self, state):
        # TODO: your code here
        return "R"

    def getTradeDecision(self, state):
	# TODO: your code here
        return None

    def endGame(self, state):
        # TODO: your code here


if __name__ == '__main__':
    url = environ.get("CBURL", u"ws://127.0.0.1:4000/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(GOATAgent)
