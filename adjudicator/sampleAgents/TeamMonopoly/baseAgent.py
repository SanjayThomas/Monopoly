import sys
import six
import abc
import json
from os import environ

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.wamp.types import PublishOptions, SubscribeOptions
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

@six.add_metaclass(abc.ABCMeta)
class BaseAgent(ApplicationSession):

	@inlineCallbacks
	def onJoin(self, details):
		print("Session attached!")
		
		#Command line args
		self.gameId = "1"
		
		#URIs
		join_game_uri = 'com.game{}.joingame'.format(self.gameId,"TeamMonopoly")
		
		# call a remote procedure
		res = yield self.call(join_game_uri)
		if res[0] == 1:
			print("The following error occurred.")
			print(res[1])
			self.leave()
			return

		self.id = res[1]
		print("The agent was assigned the id: {}".format(self.id))
		
		self.endpoints = {
			'REQUEST'   : 'monopoly.game{}.agent{}.request',
			'RESPONSE'  : 'monopoly.game{}.agent{}.response'
		}

		self.phaseToMethod = {
			'START_GAME'         : self.startGame,
			'JAIL'               : self.jailDecision,
			'BUY'                : self.buyProperty,
			'BUY_RESULT'         : self.buyResult,
			'AUCTION'            : self.auctionProperty,
			'MORTGAGE'           : self.mortgage,
			'UNMORTGAGE'         : self.unmortgage,
			'SELL_HOUSES'        : self.sellHouses,
			'TRADE'              : self.getTradeDecision,
			'TRADE_RESPONSE'     : self.respondTrade,
			'BUY_HOUSES'         : self.buyHouses,
			'END_GAME'           : self.endGame,
			'START_TURN'         : self.startTurn,
			#'JAIL_RESULT'        :
			'DICE_ROLL'          : self.diceRoll,
			#'CHANCE_CARD'        :
			#'COMMUNITY_CHEST'    :
			#'AUCTION_RESULT'     :
			#'MORTGAGE_RESULT'    :
			#'SELL_HOUSES_RESULT' :
			#'TRADE_RESULT'       :
			#'BUY_HOUSES_RESULT'  :
			'END_TURN'           : self.endTurn,
			#'BANKRUPT'           : 
		}
		
		uri = self.endpoints['REQUEST'].format(self.gameId, self.id)
		self.requestId = yield self.subscribe(self.mapper, uri, options=SubscribeOptions(get_retained=True))

		print("Successfully registered!")
	
	def getId(self):
		return self.id

	def mapper(self,state):
		result = None
		jsonState = json.loads(state)
		phase = jsonState['phase']
		print("Inside mapper for phase: {}".format(phase))
		if phase in self.phaseToMethod:
			result = self.phaseToMethod[phase](state)
		uri = self.endpoints['RESPONSE'].format(self.gameId, self.id)
		self.publish(uri, phase, result, options=PublishOptions(acknowledge=True,retain=True))

		if phase == "END_GAME" and isinstance(jsonState['phase_payload'], dict):
			#The last game has completed
			self.teardownAgent()
	
	def onDisconnect(self):
		print("Agent disconnected")
		if reactor.running:
			reactor.stop()

	def teardownAgent(self):
		# cleanup
		self.requestId.unsubscribe()
		self.leave()
	
	@abc.abstractmethod
	def startGame(self, state):
		"""
		Prepare for a new game.
		"""
	
	def startTurn(self, state):
		"""
		Merely indicating the start of a turn. No other intended function.
		"""
		pass

	def diceRoll(self, state):
		"""
		Indicates the value of dice roll for the current turn.
		"""
		pass
	
	def endTurn(self, state):
		"""
		Merely indicating the end of a turn. No other intended function.
		"""
		pass

	@abc.abstractmethod
	def jailDecision(self, state):
		"""
		Add code stating how you want to get out of jail here
		"""
	
	@abc.abstractmethod
	def buyProperty(self, state):
		"""
		Add code to decide whether to buy a property here.
		"""

	def buyResult(self, state):
		"""
		Indicates whether current player has decided to buy or auction
		"""
		pass

	@abc.abstractmethod
	def auctionProperty(self, state):
		"""
		Add code deciding your bid for an auction here.
		"""

	@abc.abstractmethod
	def mortgage(self, state):
		"""
		Mortgage properties
		"""
	
	@abc.abstractmethod
	def sellHouses(self, state):
		"""
		Sell houses or hotels
		"""
	
	@abc.abstractmethod
	def getTradeDecision(self,state):
		"""
		Add code for trade proposals here.
		"""
	
	@abc.abstractmethod
	def respondTrade(self, state):
		"""
		Add code for responding to trades here.
		"""

	@abc.abstractmethod
	def unmortgage(self, state):
		"""
		Unmortgage properties
		"""
	
	@abc.abstractmethod
	def buyHouses(self, state):
		"""
		Buy houses or hotels
		"""
	
	@abc.abstractmethod
	def endGame(self, winner):
		"""
		Process the results of a completed game.
		The very last game would be a dictionary containing the agentId's and the 
		corresponding number of wins for each of them.
		"""
