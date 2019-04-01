import six
import abc
from functools import partial

import constants
from dice import Dice
from state import State
from cards import Cards
from utils import Timer

@six.add_metaclass(abc.ABCMeta)
class Action:
	
	def __init__(self,staticContext):
		self.BOARD_SIZE = staticContext["BOARD_SIZE"]
		self.CHANCE_GET_OUT_OF_JAIL_FREE = staticContext["CHANCE_GET_OUT_OF_JAIL_FREE"]
		self.COMMUNITY_GET_OUT_OF_JAIL_FREE = staticContext["COMMUNITY_GET_OUT_OF_JAIL_FREE"]
		self.JUST_VISTING = staticContext["JUST_VISTING"]
		self.JAIL = staticContext["JAIL"]
		self.PLAY_ORDER = staticContext["PLAY_ORDER"]
		self.TOTAL_NO_OF_PLAYERS = staticContext["TOTAL_NO_OF_PLAYERS"]
		self.PASSING_GO_MONEY = staticContext["PASSING_GO_MONEY"]
		self.TOTAL_NO_OF_TURNS = staticContext["TOTAL_NO_OF_TURNS"]
		self.INITIAL_CASH = staticContext["INITIAL_CASH"]
		self.NO_OF_GAMES = staticContext["NO_OF_GAMES"]
		#self.MAX_BSM_REQUESTS = staticContext["MAX_BSM_REQUESTS"]
		#self.MAX_TRADE_REQUESTS = staticContext["MAX_TRADE_REQUESTS"]
		#self.ACTION_TIMEOUT = staticContext["ACTION_TIMEOUT"]
		
		#Maximum number of BSM requests a player can send in a BSM in a given turn
		self.MAX_BSM_REQUESTS = 10
		self.MAX_TRADE_REQUESTS = 10
		self.ACTION_TIMEOUT = 30
		self.DEFAULT_ACTIONS = {
			"JAIL_IN": ("P",),
			"BUY_IN": False,
			"AUCTION_IN": 0,
			"BSM_IN": None,
			"TRADE_IN": None,
			"RESPOND_TRADE_IN": False,
			"BROADCAST_IN": None
		}
	
	def setContext(self,context):
		self.context = context
		self.context.currentClass = self.__class__.__name__
		#to prevent repeated calls to particular subscribe
		#f = open("currentMethod.txt", "w")
		#f.write("buyProperty")
		#f.close()
		
		self.dice = context.dice
		self.chest = context.chest
		self.chance = context.chance
		self.state = context.state
		self.mortgagedDuringTrade = context.mortgagedDuringTrade
		self.winner = context.winner
	
	def publishAction(self,agentId,actionClass):
		self.timer = Timer()
		self.timer.setTimeout(partial(self.timeoutHandler,actionClass), self.ACTION_TIMEOUT)
		agent_attributes = self.context.genAgentChannels(agentId,requiredChannel = actionClass)
		self.context.publish(agent_attributes[actionClass], self.state.toJson())
	
	def timeoutHandler(self,actionClass):
		for agentId in self.agentsYetToRespond:
			#These agents have timed out. Use default actions for them.
			#TODO: Lock subscribe so that these agents can't invoke it in between
			self.subscribe(agentId,self.DEFAULT_ACTIONS[actionClass])
	
	def canAccessSubscribe(self,agentId):
		"""
		Check if the agent can access the current subscribe method at the time of invocation
		The game might have progressed to another ActionClass or another Player's turn.
		"""
		#f = open("currentMethod.txt", "r")
		#currentMethod = f.read()
		#f.close()
		#print("Current Class: "+currentClass)
		if agentId in self.agentsYetToRespond and self.context.currentClass == self.__class__.__name__:
			#we are expecting this agent to respond to this action
			#indicate that the agent has responded to this action
			self.agentsYetToRespond.remove(agentId)
			if len(self.agentsYetToRespond)==0:
				#no more agents left to respond. The timeoutHandler is not required any longer.
				self.timer.setClearTimer()
			return True
		else:
			print("Agent "+str(agentId)+" can't access the subscribe of "+self.__class__.__name__+" in "+str(self.context.currentClass))
			return False

	@abc.abstractmethod
	def publish(self):
		"""
		Publishes an action on the agent's channel.
		"""	
	
	@abc.abstractmethod
	def subscribe(self,*args,**kwargs):
		"""
		Callback invoked by the agent when it is done with an action.
		"""