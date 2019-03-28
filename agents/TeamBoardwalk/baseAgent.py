import sys
import six
import abc
from os import environ

from board import Type, Group
from state import State

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

@six.add_metaclass(abc.ABCMeta)
class BaseAgent(ApplicationSession):

	@inlineCallbacks
	def onJoin(self, details):
		print("Session attached!")
		
		#TODO: Configuration for these
		#Command line args
		self.game_id = int(sys.argv[1])
		
		#URIs
		join_game_uri = 'com.game{}.joingame'.format(self.game_id)
		
		# call a remote procedure.
		res = yield self.call(join_game_uri)
		print("The agent was assigned id: {}".format(res['agent_id']))
		
		self.pid = res['agent_id']
		self.minMoney = 200
		self.stealing = False
		
		self.bsmIn = yield self.subscribe(self.getBSMTDecision,res['BSM_IN'])
		self.buyIn = yield self.subscribe(self.buyProperty,res['BUY_IN'])
		self.auctionIn = yield self.subscribe(self.auctionProperty,res['AUCTION_IN'])
		self.jailIn = yield self.subscribe(self.jailDecision,res['JAIL_IN'])
		self.tradeIn = yield self.subscribe(self.getTradeDecision,res['TRADE_IN'])
		self.broadcastIn = yield self.subscribe(self.receiveState,res['BROADCAST_IN'])
		self.respondTradeIn = yield self.subscribe(self.respondTrade,res['RESPOND_TRADE_IN'])
		self.endGameIn = yield self.subscribe(self.endGame,res['END_GAME'])
		
		self.endpoints = res

		#Successfully Registered. Invoke confirm_register
		response = yield self.call(res['CONFIRM_REGISTER'])
		print("Result of calling confirm_register: "+str(response))
	
	def bsmListener(self,state):
		result = self.getBSMTDecision(state)
		self.publish(self.endpoints['BSM_OUT'],result)
	
	def buyListener(self,state):
		result = self.buyProperty(state)
		self.publish(self.endpoints['BUY_OUT'],result)
		
	def auctionListener(self,state):
		result = self.auctionProperty(state)
		self.publish(self.endpoints['AUCTION_OUT'],result)
	
	def jailListener(self,state):
		result = self.jailDecision(state)
		self.publish(self.endpoints['JAIL_OUT'],result)
	
	def tradeListener(self,state):
		result = self.getTradeDecision(state)
		self.publish(self.endpoints['TRADE_OUT'],result)
	
	def broadcastListener(self,state):
		result = self.receiveState(state)
		self.publish(self.endpoints['BROADCAST_OUT'],result)
	
	def respondTradeListener(self,state):
		result = self.respondTrade(state)
		self.publish(self.endpoints['RESPOND_TRADE_OUT'],result)

	def onDisconnect(self):
		print("disconnected")
		if reactor.running:
			reactor.stop()

	def endGame(self,result):
		# do some cleanup stuff if you have any
		print("************* The winner is player {} *************".format(result))
		self.bsmIn.unregister()
		self.buyIn.unregister()
		self.auctionIn.unregister()
		self.jailIn.unregister()
		self.tradeIn.unregister()
		self.broadcastIn.unregister()
		self.respondTradeIn.unregister()
		self.endGameIn.unregister()

		self.leave()
	
	@abc.abstractmethod
	def getBSMDecision(self, state):
		"""
		Add code for Buy/Sell Houses,Hotels and Mortgage/Unmortgage here.
		"""
	
	@abc.abstractmethod
	def buyProperty(self, state):
		"""
		Add code to decide whether to buy a property here.
		"""

	@abc.abstractmethod
	def auctionProperty(self, state):
		"""
		Add code deciding your bid for an auction here.
		"""
	
	@abc.abstractmethod
	def jailDecision(self, state):
		"""
		Add code stating how you want to get out of jail here
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
	def receiveState(self, state):
		"""
		Function returns several info messages. You can process them here.
		"""
